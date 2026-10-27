# Add actual KLEM research without uploading the archive

You can upload this finished repository to GitHub afterward. You do **not** need to upload your entire KLEM folder. The screenshots show a roughly 2.65 GB hourly research file; keep it on your own machine. GitHub's browser upload limit is 25 MiB per file and ordinary Git blocks files above 100 MiB. [Official file-size documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## 1. Identify one useful source

Start with a research CSV/JSONL containing decision timestamps, market tickers, contemporaneous prices/features and official settlement labels. Do not begin with live account logs or private keys. The supplied screenshots show file names, but not their schemas. This release cannot know which KLEM version uses which key names.

Inspect keys locally without displaying values:

```python
import json
from pathlib import Path
with Path(r"C:\your-folder\klem2_research.jsonl").open(encoding="utf-8-sig") as source:
    first_record = json.loads(next(source))
print(sorted(first_record.keys()))
```

Do not paste full live records into a public issue. The importer supports flat JSONL objects or CSV headers. Nested formats need a local flattening adapter. Missing official outcomes need a local join to an authoritative settlement export. Do not guess or derive official outcomes from local P&L.

## 2. Map explicit units and meanings

`research/mapping.example.json` maps **canonical key → source key**. Edit the right-hand values after inspecting the actual schema.

| Canonical key | Required meaning |
| --- | --- |
| ticker | Public market identifier, letters/numbers/dot/dash/underscore only |
| timestamp | Decision/observation timestamp, ISO 8601 with timezone |
| settlement_time | Official market settlement timestamp after the observation |
| probability | Quoted **YES** probability, fraction strictly between 0 and 1 |
| outcome | Official **YES** settlement result, 0 or 1 |
| side | Selected side, YES or NO |
| ttx_minutes | Positive minutes until settlement; within one minute of timestamps |
| atr | Nonnegative contemporaneous ATR, using one documented consistent unit |
| normalized_distance | Finite contemporaneous normalized distance |
| momentum | Finite contemporaneous momentum, using one documented definition |

Session and weekday are derived from the UTC timestamp. Source values are ignored. Unknown keys are discarded.

If source prices are in cents, divide by 100 in a local adapter. If source probability is for NO, convert to YES in that adapter. There is deliberately no heuristic guessing. Do not invent missing ATR/momentum values. If a source lacks these fields, add an explicit nullable-feature schema version and corresponding UI handling before using it here.

## 3. Import locally

Windows PowerShell, from the project directory:

```powershell
py -m marketlab ingest "C:\KLEM\klem2_research.jsonl" --mapping research/mapping.example.json
py -m marketlab export --limit 5000 --output data/public/imported.json
py -m marketlab build --input data/public/imported.json
py -m http.server 8000 --directory dist
```

macOS/Linux can use `python` and normal POSIX paths. No input is uploaded by these commands.

The import produces a local ignored `data/private/research.sqlite`. It hashes the source in a bounded first pass, then parses records in a second pass. Very large files therefore need enough time for two reads and enough disk for normalized records/indexes. JSONL lines above 2 MB abort the transaction. CSV fields are bounded by Python's CSV parser. Error reports expose row numbers and generic errors, not record contents.

Run one importer process at a time. Accepted records, exact duplicates and rejected records are counted. Conflicting records at the same ticker/time are rejected. Inconsistent settlement identity across observations of one ticker is also rejected. Review rejection counts before exporting. A later file with a conflicting settlement does not silently overwrite the earlier official outcome; resolve that source conflict in a clean database.

## 4. Review and commit the small output

The exporter chooses the earliest observation per ticker and then evenly spaced canonical markets over the observed timeline. It includes the first and last market. This is a deterministic public **sample**, not a lossless archive or unbiased full-universe estimator.

Inspect `data/public/imported.json`, confirm all fields are appropriate for public release, and verify the feature definitions and as-of calculations. Allowlisting removes unknown fields but does not prove known fields are nonproprietary.

Set `research/build-config.json` to `{"dataset":"data/public/imported.json"}`, rebuild, and rerun tests. Commit the reviewed small JSON, configuration, code and generated `dist/`. The browser's source fingerprint identifies its downloadable sanitized input, not the entire raw archive. `source_sha256` retains the raw-file fingerprints in exported metadata.

## 5. Verify historical claims separately

Importing 5,000 sample records does not verify a 20,522-market archive or a 756-trade evaluation. For each claim in `research/claims.json`, retain:

- Exact dataset/run identifier and source artifact SHA-256.
- Record unit: market, ticker, observation, candidate or trade.
- Filters, date coverage and research/test boundary.
- Formula and script that reproduces the value.
- Cost treatment and denominators for any return metric.

The current UI intentionally presents this register as unverified. A future verification integration should render approved report outputs with provenance; do not manually promote claims by changing a label.
