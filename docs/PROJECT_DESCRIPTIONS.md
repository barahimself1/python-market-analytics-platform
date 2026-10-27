# Employer-facing project materials

These drafts describe the delivered implementation. Use them after reviewing the code and being prepared to explain the methods. The public demo is synthetic; none of these drafts presents it as real KLEM performance. Add actual scale or performance figures only after reproducing them from specific source artifacts.

## Repository description

Python research workstation for prediction-market calibration, chronological validation, feature analysis, execution-cost scenarios and settlement reconciliation.

## Recruiter summary

Built a Python market-research pipeline and interactive analytical workstation with streaming CSV/JSONL ingestion, SQLite storage, strict schema validation, chronological holdouts, calibration intervals and execution-cost scenarios. The public product emphasizes reproducibility and evidence provenance, with synthetic demonstration data and an explicit path for sanitized research imports.

## LinkedIn project description

Python Market Analytics Research Platform is a research workstation for turning prediction-market observations into inspectable evidence. The system combines streaming Python ingestion, disk-backed deduplication and schema validation with interactive calibration, feature comparisons, chronological validation and execution-cost analysis.

I structured the evaluation around one observation per market, settlement-aware time boundaries, expanding-window diagnostics and block-bootstrap uncertainty. The interface also demonstrates settlement-reconciliation checks and records exploration settings with dataset fingerprints. The public release uses clearly labeled synthetic data; broader KLEM historical findings remain separate until verified against their source artifacts.

## Resume options — select two or three, not all

**Data / software engineering**

- Built a Python ingestion and analytics pipeline for CSV/JSONL market records using streaming validation, disk-backed SQLite deduplication, source fingerprints and deterministic public exports.
- Developed a responsive research workstation with 14 sections, interactive filters, CSV exports, execution-cost scenarios and browser-local experiment snapshots; prepared for deployment through a tested static build workflow.

**Quantitative research / analytics**

- Implemented settlement-aware chronological holdouts, four expanding evaluation windows, probability calibration with Wilson intervals and a reproducible 1,000-resample moving-block bootstrap.
- Designed feature exploration with decision-time allowlists, research/test comparisons and explicit small-sample warnings to distinguish exploratory relationships from confirmed out-of-sample findings.

**Product / systems engineering**

- Translated a market-research workflow into an interactive analytical product spanning data inspection, validation, execution assumptions and settlement reconciliation, with dataset-level provenance throughout.
- Defined and tested public-data contracts, temporal validation boundaries and exception handling across a modular Python pipeline and custom browser interface.

Do not claim exchange API integration, real fills, live monitoring, specific KLEM historical scale or verified profitability from this release alone. The deployment bullet should say “prepared a deployment workflow” until you actually publish it.

## Suggested GitHub topics

python, market-data, data-engineering, quantitative-research, prediction-markets, calibration, time-series, sqlite, data-validation, research-tools, fintech, javascript, reproducible-research

## Portfolio metadata

- **Title:** Python Market Analytics Research Platform
- **Product name:** MarketLab
- **Author:** Bara Mbaye
- **Category:** Data engineering / research software / analytical product
- **Stack:** Python, SQLite, JavaScript, SVG, HTML/CSS, GitHub Actions
- **Demo status:** Synthetic, seeded and clearly labeled
- **Deployment status:** Packaged locally; live URL pending user deployment
- **Core theme:** Evidence provenance and chronological research discipline
- **Historical system:** KLEM, described in the supplied brief; underlying implementation not attached
