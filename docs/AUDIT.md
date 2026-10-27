# Release audit — 26 October 2026

## Verification performed

- **41 Python tests passed** with `python -m unittest discover -s tests -v`.
- **9 Node tests passed** with `node --test tests/analytics.test.cjs`.
- `node --check web/app.js` passed after the interface was assembled; the final script was then exercised in browser.
- Deterministic build, sanitized-download hash identity, Python/JavaScript numerical parity, import/export round trips, chronology, label purging, conflicting records, malformed input, calibration, bootstrap and reconciliation were tested.
- All 14 navigation sections rendered in the browser. Market-period filtering, record details, zero-result search, feature selection, saved exploration records, calibration bucket changes and zero-fill execution scenarios were exercised.
- A browser-generated filtered CSV was read back locally: **216 records, all marked `test`**.
- Desktop overview and architecture were visually inspected. A **390 × 844 embedded mobile viewport** was inspected, including menu open/close by navigation and calibration controls. This is responsive-layout QA, not a physical-device certification.
- Captured screenshots are under `screenshots/`. The temporary mobile test harness is excluded from the deliverable.

## Code quality

The Python schema, analytics, ingestion, fixture generation, build and CLI are separate modules. UI analytics are pure functions with Node tests and parity checks against compiled Python outputs. Production behavior needs no external packages. The importer and exporter bound Python memory use; SQLite handles disk-backed grouping and sorting.

The browser UI is vanilla JavaScript with a common state and rendering layer. Its 14 page renderers live in one file for a simple static build; further UI growth should split those renderers into dedicated modules. `pyproject.toml` describes the source project, but the supported workflow is running from the extracted repository, where data and web assets are present; no wheel distribution is delivered.

The provided GitHub Actions workflows have not been run on GitHub in this session. Their shell test/build commands were run locally. CI validates calculations and scans files; it does not automate the browser checks above.

## Security review

The limited pattern scan completed with **no credential-pattern matches** in the public deliverable. No input credentials, account data, live execution source or raw research archives were available or included. Unknown record fields and top-level public metadata are stripped; tests exercise that boundary. Script data escapes `<`; UI values are HTML-escaped; CSV formula prefixes are neutralized. The static app has no network data fetches or live controls.

This was a local code review and heuristic scan, not an independent penetration test or complete secret-scanning certification. The scanner intentionally excludes private/raw directories and cannot certify previously tracked Git history. Real data needs a fresh source-specific privacy and proprietary-information review before publication.

## Usability review

The interface provides labeled controls, visible focus outlines, a skip link, native dialog focus handling, responsive navigation, empty states, sample-size warnings and explicit synthetic/imported badges. Tables can scroll horizontally without forcing the whole page wider. Charts have textual descriptions, tabular alternatives and hover details. Formal WCAG conformance, cross-browser testing and screen-reader certification were not performed.

Dates are UTC for reproducible analysis. Navigating between sections resets sample filters; the selected feature and execution assumptions persist within the session. The fixed Validation Lab always analyzes the compiled dataset and explicitly ignores explorer filters. Experiment snapshots are browser-local and can be exported; they are not a shared experiment database.

## Factual consistency review

The attached brief and three directory screenshots were inspected. No actual KLEM scripts, logs, reports or datasets were attached. All historical counts and performance figures remain unverified in a separate register. Nothing in this build verifies the 20,522-market archive, 2,139-ticker dataset, 756-trade evaluation, historical search equivalence or reported performance.

The default demonstration is a deterministic fictional dataset of 720 markets. The verified fixture split is 504 research / 216 test, with no purged rows. Reconciliation is independently labeled as fictional even if the active dataset is later imported.

No historical paths, latency model, actual fills, upstream exchange ingestion or private strategy were fabricated. The source evidence register distinguishes visible filenames from unobserved implementation content.

## Remaining source-dependent work

1. Map the actual KLEM field names, units and nested structures to the public contract.
2. Verify feature availability at decision time and official settlement provenance.
3. Reproduce each desired historical claim from its specific report or ledger.
4. Review the sanitized output before committing it.
5. Upload and deploy the package, then add the verified live URL to the README and portfolio.

This handoff is a new local repository package. It has not modified an existing repository, migrated a live Streamlit application, or published a public deployment.
