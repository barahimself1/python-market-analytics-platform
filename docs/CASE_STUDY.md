# From research archives to an inspectable product

The Python Market Analytics Research Platform addresses a common research problem: a favorable chart often hides the dataset boundary, feature timing, sample size and execution assumptions that determine whether a finding is credible.

The broader KLEM project brief describes prediction-market research across data ingestion, historical reconstruction, feature exploration, forward evaluation, monitoring and settlement reconciliation. This public build makes the analytical discipline inspectable without publishing account credentials or private execution code.

The implementation separates three concerns. A Python importer validates flat CSV/JSONL records and stores allowed fields in SQLite. A compiler creates a deterministic public sample and precomputes validation outputs. A custom static frontend exposes the sample through a coherent workstation rather than disconnected charts.

The hardest design decision was evidentiary. Only a brief and folder screenshots were supplied, so there was no legitimate way to reconstruct historical results. Instead, the application ships with a labeled deterministic fixture, keeps user-supplied claims in a separate unverified register, and exposes an explicit real-data import contract. That allows the software to work now without turning missing evidence into invented statistics.

Temporal validity shapes the implementation. It reduces repeated observations to one canonical row per ticker, keeps equal decision times together at the research/test boundary, and purges research labels unsettled at the test start. Feature selectors exclude outcomes and realized returns. The interface treats same-direction performance as unconfirmed rather than automatically awarding a persistence label.

Operational realism is represented narrowly and honestly. Interactive execution scenarios show fees, adverse entry slippage and expected fill participation. They do not pretend to reproduce latency or queue dynamics without timestamped quote and fill data. Separate fictional reconciliation fixtures expose duplicate, missing, pending and inconsistent settlement records.

The custom interface is deployed as static files. Python is needed for reproducible builds, not for a continuously running server. Browser-side filtered calculations are tested against Python results. This reduces deployment cost and dependency surface while retaining a clear engineering story.

The delivered result is a working research product and ingestion foundation. The next source-dependent milestone is to map a sanitized real KLEM dataset, audit feature timestamps, reproduce the claimed research figures from specific reports, and attach that evidence to the public product. No historical performance finding is asserted by this release.
