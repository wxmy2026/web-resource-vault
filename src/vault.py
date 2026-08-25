"""Discovery, safe streaming download, deduplication, and provenance storage."""

from __future__ import annotations

import hashlib
import json
import logging
import mimetypes
import os
import re
import tempfile
import threading
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from typing_extensions import Self
from urllib3.util.retry import Retry

LOGGER = logging.getLogger("web_resource_vault")

RESOURCE_EXTENSIONS = {
    ".pdf", ".epub", ".txt", ".md", ".csv", ".json",
    ".mp3", ".m4a", ".wav", ".ogg",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".zip",
}

MIME_EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
    "application/json": ".json",
    "application/zip": ".zip",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/ogg": ".ogg",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class VaultError(RuntimeError):
    """Base exception for predictable vault failures."""


class DownloadError(VaultError):
    """A remote resource could not be downloaded safely."""


class RobotsDenied(VaultError):
    """robots.txt disallows the requested URL for this client."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Only absolute HTTP(S) URLs are supported: {url!r}")
    return urlunparse((parsed.scheme.lower(), parsed.netloc, parsed.path or "/", parsed.params, parsed.query, ""))


def clean_filename(value: str, fallback: str = "resource") -> str:
    value = unicodedata.normalize("NFKC", unquote(value or ""))
    value = value.replace("\\", "/").rsplit("/", 1)[-1]
    value = re.sub(r"[\x00-\x1f\x7f<>:\"/\\|?*]+", "_", value).strip(" .")
    if not value or value in {".", ".."}:
        value = fallback
    stem, suffix = os.path.splitext(value)
    if len(value.encode("utf-8")) > 240:
        suffix = suffix[:20]
        budget = max(1, 220 - len(suffix.encode("utf-8")))
        stem = stem.encode("utf-8")[:budget].decode("utf-8", "ignore")
        value = stem + suffix
    return value


def content_disposition_filename(header: str | None) -> str | None:
    if not header:
        return None
    message = Message()
    message["content-disposition"] = header
    filename = message.get_filename()
    return clean_filename(filename) if filename else None


def content_type(response: requests.Response) -> str:
    return response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()


def url_extension(url: str) -> str:
    return Path(unquote(urlparse(url).path)).suffix.lower()


def category_for(mime_type: str, filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if mime_type.startswith("audio/") or extension in {".mp3", ".m4a", ".wav", ".ogg"}:
        return "audio"
    if mime_type.startswith("image/") or extension in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "images"
    if mime_type.startswith("text/") or extension in {".txt", ".md", ".csv", ".json"}:
        return "text"
    if mime_type == "application/pdf" or extension == ".pdf":
        return "pdf"
    return "other"


@dataclass(frozen=True)
class DownloadResult:
    source_url: str
    final_url: str
    filename: str
    mime_type: str
    sha256: str
    local_path: str
    retrieved_at: str
    referrer: str | None
    size_bytes: int
    etag: str | None = None
    last_modified: str | None = None
    duplicate: bool = False
    not_modified: bool = False

    def as_record(self) -> dict[str, Any]:
        return asdict(self)


class ResourceVault:
    """Collect public resources into a provenance-aware local vault."""

    def __init__(
        self,
        root: str | Path = "vault",
        *,
        timeout: tuple[float, float] = (10.0, 60.0),
        max_bytes: int = 1_073_741_824,
        obey_robots: bool = True,
        user_agent: str = "WebResourceVault/0.2 (+https://github.com/wxmy2026/web-resource-vault)",
        retries: int = 3,
    ) -> None:
        self.root = Path(root)
        self.files_dir = self.root / "files"
        self.temp_dir = self.root / ".tmp"
        self.manifest_path = self.root / "manifest.json"
        self.index_path = self.root / "index.jsonl"
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.obey_robots = obey_robots
        self.user_agent = user_agent
        self._manifest_lock = threading.RLock()
        self._robots_cache: dict[str, RobotFileParser] = {}

        self.root.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD"}),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _robots_parser(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        cached = self._robots_cache.get(origin)
        if cached:
            return cached
        robots_url = origin + "/robots.txt"
        parser = RobotFileParser(robots_url)
        try:
            response = self.session.get(robots_url, timeout=self.timeout, allow_redirects=True)
            if response.status_code == 200:
                parser.parse(response.text.splitlines())
            else:
                parser.parse([])
        except requests.RequestException as exc:
            LOGGER.warning("Could not read %s (%s); continuing with an empty policy", robots_url, exc)
            parser.parse([])
        self._robots_cache[origin] = parser
        return parser

    def _check_robots(self, url: str) -> None:
        if self.obey_robots and not self._robots_parser(url).can_fetch(self.user_agent, url):
            raise RobotsDenied(f"robots.txt disallows: {url}")

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"schema_version": 1, "updated_at": utc_now(), "resources": []}
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VaultError(f"Manifest is unreadable; it was left untouched: {exc}") from exc
        if not isinstance(data.get("resources"), list):
            raise VaultError("Manifest has an invalid resources field")
        return data

    @staticmethod
    def _atomic_text(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

    def _write_metadata(self, data: dict[str, Any]) -> None:
        data["updated_at"] = utc_now()
        manifest = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        index = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in data["resources"])
        self._atomic_text(self.manifest_path, manifest)
        self._atomic_text(self.index_path, index)

    def rebuild_manifest(self) -> dict[str, Any]:
        """Validate the canonical manifest and atomically regenerate both metadata files."""
        with self._manifest_lock:
            data = self._load_manifest()
            self._write_metadata(data)
            return data

    def _existing_for_source(self, source_url: str) -> dict[str, Any] | None:
        data = self._load_manifest()
        for item in reversed(data["resources"]):
            if item.get("source_url") == source_url:
                return item
        return None

    def _choose_filename(self, response: requests.Response, mime_type: str) -> str:
        filename = content_disposition_filename(response.headers.get("Content-Disposition"))
        if not filename:
            filename = clean_filename(Path(unquote(urlparse(response.url).path)).name, "resource")
        if not Path(filename).suffix and mime_type in MIME_EXTENSIONS:
            filename += MIME_EXTENSIONS[mime_type]
        elif not Path(filename).suffix:
            guessed = mimetypes.guess_extension(mime_type) if mime_type else None
            filename += guessed or ".bin"
        return filename

    @staticmethod
    def _validate_payload(mime_type: str, filename: str, first_bytes: bytes) -> None:
        lowered = first_bytes[:512].lstrip().lower()
        if mime_type in {"text/html", "application/xhtml+xml"} or lowered.startswith((b"<!doctype html", b"<html")):
            raise DownloadError("The URL returned an HTML page; use `crawl` for resource pages")
        extension = Path(filename).suffix.lower()
        if extension not in RESOURCE_EXTENSIONS and mime_type not in MIME_EXTENSIONS:
            LOGGER.warning("Saving an unrecognized resource type as %s", filename)
        if extension == ".pdf" and first_bytes and not first_bytes.startswith(b"%PDF-"):
            raise DownloadError("The server named the response as PDF, but its signature is not PDF")

    def _commit_download(
        self,
        temporary: Path,
        *,
        source_url: str,
        final_url: str,
        filename: str,
        mime_type: str,
        digest: str,
        size_bytes: int,
        referrer: str | None,
        etag: str | None,
        last_modified: str | None,
    ) -> DownloadResult:
        with self._manifest_lock:
            data = self._load_manifest()
            duplicate_item = next((item for item in data["resources"] if item.get("sha256") == digest), None)
            duplicate = duplicate_item is not None
            if duplicate_item:
                local_path = duplicate_item["local_path"]
                temporary.unlink(missing_ok=True)
            else:
                domain = clean_filename(urlparse(final_url).hostname or "unknown-host")
                category = category_for(mime_type, filename)
                destination_dir = self.files_dir / domain / category
                destination_dir.mkdir(parents=True, exist_ok=True)
                destination = destination_dir / filename
                if destination.exists():
                    destination = destination.with_name(f"{destination.stem}-{digest[:8]}{destination.suffix}")
                os.replace(temporary, destination)
                local_path = destination.relative_to(self.root).as_posix()

            result = DownloadResult(
                source_url=source_url,
                final_url=final_url,
                filename=Path(local_path).name,
                mime_type=mime_type,
                sha256=digest,
                local_path=local_path,
                retrieved_at=utc_now(),
                referrer=referrer,
                size_bytes=size_bytes,
                etag=etag,
                last_modified=last_modified,
                duplicate=duplicate,
            )
            record = result.as_record()
            matching = next(
                (i for i, item in enumerate(data["resources"]) if item.get("source_url") == source_url and item.get("sha256") == digest),
                None,
            )
            if matching is None:
                data["resources"].append(record)
            else:
                data["resources"][matching] = record
            self._write_metadata(data)
            return result

    def add(self, url: str, *, referrer: str | None = None) -> DownloadResult:
        source_url = normalize_url(url)
        self._check_robots(source_url)
        existing = self._existing_for_source(source_url)
        headers: dict[str, str] = {}
        if existing and existing.get("etag"):
            headers["If-None-Match"] = existing["etag"]
        if existing and existing.get("last_modified"):
            headers["If-Modified-Since"] = existing["last_modified"]

        LOGGER.info("Downloading %s", source_url)
        temporary_path: Path | None = None
        try:
            with self.session.get(source_url, stream=True, timeout=self.timeout, allow_redirects=True, headers=headers) as response:
                if response.status_code == 304 and existing:
                    return DownloadResult(**{**existing, "not_modified": True})
                try:
                    response.raise_for_status()
                except requests.HTTPError as exc:
                    raise DownloadError(f"HTTP {response.status_code} for {source_url}") from exc

                mime_type = content_type(response)
                filename = self._choose_filename(response, mime_type)
                declared_length = response.headers.get("Content-Length")
                if declared_length and declared_length.isdigit() and int(declared_length) > self.max_bytes:
                    raise DownloadError(f"Resource exceeds max size of {self.max_bytes} bytes")

                descriptor, temporary_name = tempfile.mkstemp(prefix="download-", suffix=".part", dir=self.temp_dir)
                temporary_path = Path(temporary_name)
                digest = hashlib.sha256()
                total = 0
                first = bytearray()
                with os.fdopen(descriptor, "wb") as handle:
                    for chunk in response.iter_content(chunk_size=128 * 1024):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > self.max_bytes:
                            raise DownloadError(f"Resource exceeded max size of {self.max_bytes} bytes")
                        if len(first) < 512:
                            first.extend(chunk[: 512 - len(first)])
                        digest.update(chunk)
                        handle.write(chunk)
                    handle.flush()
                    os.fsync(handle.fileno())
                if total == 0:
                    raise DownloadError("The server returned an empty response")
                self._validate_payload(mime_type, filename, bytes(first))
                return self._commit_download(
                    temporary_path,
                    source_url=source_url,
                    final_url=normalize_url(response.url),
                    filename=filename,
                    mime_type=mime_type or "application/octet-stream",
                    digest=digest.hexdigest(),
                    size_bytes=total,
                    referrer=referrer,
                    etag=response.headers.get("ETag"),
                    last_modified=response.headers.get("Last-Modified"),
                )
        except requests.RequestException as exc:
            raise DownloadError(f"Network error for {source_url}: {exc}") from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def discover(self, page_url: str, *, max_page_bytes: int = 5_242_880) -> list[str]:
        page_url = normalize_url(page_url)
        self._check_robots(page_url)
        try:
            with self.session.get(page_url, stream=True, timeout=self.timeout, allow_redirects=True) as response:
                response.raise_for_status()
                mime_type = content_type(response)
                if mime_type and mime_type not in {"text/html", "application/xhtml+xml"}:
                    raise DownloadError(f"Discovery URL is not HTML ({mime_type})")
                body = bytearray()
                for chunk in response.iter_content(64 * 1024):
                    body.extend(chunk)
                    if len(body) > max_page_bytes:
                        raise DownloadError(f"Discovery page exceeds {max_page_bytes} bytes")
                base_url = response.url
                encoding = response.encoding or response.apparent_encoding or "utf-8"
        except requests.RequestException as exc:
            raise DownloadError(f"Could not read discovery page {page_url}: {exc}") from exc

        soup = BeautifulSoup(bytes(body), "html.parser", from_encoding=encoding)
        found: set[str] = set()
        for element, attribute in (("a", "href"), ("audio", "src"), ("source", "src")):
            for node in soup.find_all(element):
                raw = node.get(attribute)
                if not raw:
                    continue
                absolute = urljoin(base_url, raw)
                try:
                    normalized = normalize_url(absolute)
                except ValueError:
                    continue
                if url_extension(normalized) in RESOURCE_EXTENSIONS:
                    found.add(normalized)
        return sorted(found)

    def crawl(self, page_url: str) -> list[DownloadResult]:
        page_url = normalize_url(page_url)
        results: list[DownloadResult] = []
        for resource_url in self.discover(page_url):
            try:
                results.append(self.add(resource_url, referrer=page_url))
            except VaultError as exc:
                LOGGER.error("Skipping %s: %s", resource_url, exc)
        return results

    def batch(self, urls: Iterable[str]) -> Iterator[tuple[str, DownloadResult | Exception]]:
        for raw in urls:
            url = raw.strip()
            if not url or url.startswith("#"):
                continue
            try:
                yield url, self.add(url)
            except (VaultError, ValueError) as exc:
                yield url, exc
