# Public/private boundary

This application needs no credentials and contains no live order controls. Its public data is a synthetic fixture until an explicitly reviewed import is selected.

## Never commit

- `.env` files, API credentials, bearer tokens or exchange signing keys.
- PEM/key/P12 files or credential-bearing configuration.
- Raw hourly or 15-minute research archives without a separate review.
- Live order, fill, balance, account or position logs.
- Account identifiers, personal financial records or private contact details.
- `positions`, `market_state`, live-session state, locks and SQLite databases.
- Proprietary strategy parameters, private rules or execution modules merely to support a public chart.
- Generated support/debug dumps that contain any of the above.

The `.gitignore` is a guardrail, not a comprehensive classifier. It cannot remove secrets already in Git history. If a credential was previously published, revoke/rotate it and follow the relevant provider's incident process.

## Implemented controls

- Explicit field allowlist and strict ticker format at ingestion.
- No raw records in rejection logs; only bounded row-number examples.
- No arbitrary metadata copied into compiled public input.
- JSON script serialization escapes `<`; all dynamic UI strings are HTML-escaped.
- CSV exports neutralize leading formula characters.
- Content Security Policy restricts scripts to local assets and disables browser network connections and form submissions.
- Private archive and database directories excluded from Git.
- Dependency-free production code; no third-party CDN assets, telemetry or API calls.

`python -m marketlab.audit` scans tracked-style public files for selected credential patterns, unexpected large files and private file types. It is a limited heuristic, not a comprehensive secret scanner or independent security assessment. Re-run after importing real data and manually inspect allowed fields for private/proprietary meaning. Use your normal repository secret-scanning service before publication.

The local Python HTTP server is a development preview, not an authenticated server for private data. Serve **only `dist/`**, never the whole KLEM directory.
