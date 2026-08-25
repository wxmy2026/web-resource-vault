# Web Resource Vault

A provenance-first Python CLI for collecting **legal, publicly accessible** learning and research resources. It discovers supported files on ordinary web pages, downloads them without buffering whole files in memory, deduplicates by SHA-256, and maintains machine-readable indexes.

It does not bypass paywalls, authentication, DRM, access controls, or licensing restrictions.

This repository is also the first stage of a broader **Personal AI Workbench**: collect trustworthy material first, then connect it to Obsidian, AnythingLLM, Anki, and later automation. The staged plan is in [`docs/ROADMAP.md`](docs/ROADMAP.md), and the free/paid comparison is in [`docs/TOOL_MATRIX.md`](docs/TOOL_MATRIX.md).

## Mac one-click setup

The repository includes a double-clickable macOS setup file for the first-stage desktop stack:

- Obsidian
- Anki Desktop
- Krita
- AnythingLLM Desktop
- this project's Python dependencies

After downloading the repository on a Mac, open `scripts/setup-mac.command`. macOS may ask for the computer password while Homebrew installs software. The script creates the resource directory at `~/PersonalAI/Vault` and does not install ComfyUI, FreshRSS, Open WebUI, or synchronization software in the first pass.

## What it does

- Downloads direct PDF, EPUB, text, data, audio, image, and ZIP resources.
- Crawls a public HTML resource page for supported links.
- Streams into a temporary file while calculating SHA-256.
- Follows redirects, retries transient HTTP failures, and enforces time/size limits.
- Uses `Content-Disposition`, URL paths, MIME types, and file signatures to name and validate downloads.
- Rejects HTML login/error pages masquerading as files.
- Deduplicates file bytes while retaining a provenance record for each source URL.
- Uses ETag and Last-Modified validators on later downloads when servers provide them.
- Obeys `robots.txt` by default and never sends credentials or cookies supplied by the user.
- Atomically replaces `manifest.json` and `index.jsonl`; `manifest` repairs a stale index after interruption.

## Install

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

## Use

```bash
# One direct file
python -m src.cli add "https://example.org/file.pdf"

# Discover supported links on a resource page, then download them
python -m src.cli crawl "https://example.org/resources"

# One direct URL per line; blank lines and # comments are ignored
python -m src.cli batch examples/urls.txt

# Validate the canonical manifest and regenerate both index files
python -m src.cli manifest
```

Global options go before the command:

```bash
python -m src.cli --root my-vault --max-mib 250 --timeout 45 -v add URL
```

`--ignore-robots` is available for a source you own or have explicit permission to retrieve. It does not grant permission or bypass access controls.

## Output

```text
vault/
  files/
    domain.example/
      pdf/
      audio/
      images/
      text/
      other/
  index.jsonl
  manifest.json
```

Every record contains at least:

- `source_url` and redirect-resolved `final_url`
- `filename`, `mime_type`, `size_bytes`, and `sha256`
- vault-relative `local_path`
- UTC `retrieved_at` and optional `referrer`
- optional `etag` and `last_modified`

`manifest.json` is canonical. `index.jsonl` contains the same resource records, one per line, for streaming ingestion by search and knowledge-base tools. If a process is interrupted between the two atomic replacements, run `manifest` to reconcile them.

## Supported discovery extensions

PDF, EPUB, TXT, MD, CSV, JSON, MP3, M4A, WAV, OGG, PNG, JPG/JPEG, WEBP, GIF, and ZIP. Direct `add` also accepts an extensionless URL when its HTTP response is a valid non-HTML resource.

## Architecture and adapters

The current core keeps the network/discovery layer, validation/downloading layer, SHA-256 deduplication, and manifest storage behind `ResourceVault`. External knowledge bases should consume `manifest.json` through a separate adapter. Do not put ChatGPT Library, Google Drive, or Notion credentials inside the downloader.

Suggested next adapters:

```text
adapters/
  chatgpt_library.py
  google_drive.py
  notion.py
```

An adapter should read vault-relative paths plus provenance records, upload through its platform's supported authorization flow, and save remote IDs outside the canonical download metadata.

## IELTS use

Start with official, intentionally free resources from IELTS.org, British Council, IDP IELTS, Cambridge English, governments, universities, and clearly licensed open educational repositories. Build a progression from A1/A2 to B1, IELTS Foundation, and then full IELTS material. Do not collect scanned commercial coursebooks or unauthorized test-book copies.

`examples/urls.txt` intentionally contains comments rather than brittle sample downloads. Add verified direct URLs from official resource pages, or pass the official page to `crawl`.

## Test

```bash
python -m unittest discover -v
```

Tests use only a local HTTP server and cover redirects, query-string discovery, `Content-Disposition`, streaming persistence, SHA-256 deduplication, HTML rejection, temporary-file cleanup, and index rebuilding.

## License

MIT. The license covers this software, not third-party resources downloaded with it. You remain responsible for source terms and copyright.
