---
name: web-resource-vault
description: Discover, download, deduplicate, index, and preserve provenance for legal public web resources such as PDFs, audio, text, datasets, and study materials. Use for building a reusable local resource vault; do not use to bypass payment, login, DRM, licensing, or access controls.
---

# Web Resource Vault

Collect openly accessible resources into a traceable local vault with this repository's CLI.

## Workflow

1. Search for suitable resources, preferring official publishers, governments, universities, standards bodies, and clearly licensed open repositories.
2. Verify that each resource is intentionally public. Do not infer authorization merely because a file URL is guessable.
3. Use `python -m src.cli add URL` for a direct resource, `crawl URL` for a public resource page, or `batch FILE` for verified direct URLs.
4. Keep robots compliance enabled. Use `--ignore-robots` only for a source the user owns or has explicit permission to retrieve.
5. Run `python -m src.cli manifest` after an interrupted job and before handing the vault to an ingestion adapter.
6. Use `vault/manifest.json` as the canonical provenance map and `vault/index.jsonl` for streaming ingestion.
7. When an authorized ChatGPT Library, Google Drive, Notion, or other knowledge-base writer exists, upload through a separate adapter or connector. Keep platform credentials and remote-object state outside the downloader.

Stop and report the exact item when a source requires payment, login, DRM circumvention, access-control bypass, or lacks a reasonable basis for public redistribution. Partial completion with clear provenance is preferable to substituting unauthorized copies.

## IELTS routing

Prefer IELTS.org, British Council, IDP IELTS, Cambridge English, and other clearly authorized free sources. Collect sample tests, audio, transcripts, band descriptors, criteria, examiner guidance, and A1–B1 foundation material. Do not download unauthorized scans of commercial IELTS books.

When selecting practice, use the learner's recent results to target roughly 70% comprehensible material and 30% challenge, progressing through A1, A2, B1, IELTS Foundation, and IELTS 4.5–5.5 before full exam difficulty.
