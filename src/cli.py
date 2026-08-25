"""Command-line interface for Web Resource Vault."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .vault import ResourceVault, VaultError

LOGGER = logging.getLogger("web_resource_vault.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="web-resource-vault", description="Collect and index legal public web resources")
    parser.add_argument("--root", default="vault", help="vault directory (default: vault)")
    parser.add_argument("--timeout", type=float, default=60.0, help="response timeout in seconds")
    parser.add_argument("--max-mib", type=float, default=1024.0, help="maximum size per resource in MiB")
    parser.add_argument("--ignore-robots", action="store_true", help="ignore robots.txt only when you have permission")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="download one direct resource URL")
    add.add_argument("url")

    crawl = commands.add_parser("crawl", help="discover and download supported links from an HTML page")
    crawl.add_argument("url")

    batch = commands.add_parser("batch", help="download direct URLs from a text file")
    batch.add_argument("url_file", type=Path)

    commands.add_parser("manifest", help="validate manifest.json and rebuild index.jsonl atomically")
    return parser


def emit(record: object) -> None:
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    level = logging.DEBUG if args.verbose > 1 else logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")
    vault = ResourceVault(
        args.root,
        timeout=(10.0, args.timeout),
        max_bytes=int(args.max_mib * 1024 * 1024),
        obey_robots=not args.ignore_robots,
    )
    failures = 0
    try:
        if args.command == "add":
            emit(vault.add(args.url).as_record())
        elif args.command == "crawl":
            records = vault.crawl(args.url)
            for record in records:
                emit(record.as_record())
            if not records:
                LOGGER.warning("No downloadable resource links were found")
        elif args.command == "batch":
            try:
                lines = args.url_file.read_text(encoding="utf-8").splitlines()
            except OSError as exc:
                LOGGER.error("Cannot read %s: %s", args.url_file, exc)
                return 2
            for url, outcome in vault.batch(lines):
                if isinstance(outcome, Exception):
                    failures += 1
                    LOGGER.error("%s: %s", url, outcome)
                else:
                    emit(outcome.as_record())
        elif args.command == "manifest":
            data = vault.rebuild_manifest()
            emit({"resources": len(data["resources"]), "manifest": str(vault.manifest_path), "index": str(vault.index_path)})
    except (VaultError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 1
    finally:
        vault.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
