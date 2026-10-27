# Methodology and numerical contract

## Market and trade semantics

Every row represents an observation of a binary market. `probability` is the YES quote, `outcome` is the official YES settlement. For a YES contract, cost = p and payoff = y. For a NO contract, cost = 1−p and payoff = 1−y. Gross return is payoff minus cost in dollars per $1 contract. This is a hypothetical mark-to-settlement result, not a verified executed trade. No win rate shown here is a KLEM strategy result.

Calibration evaluates p against y, regardless of selected side. The Brier score is mean((p−y)²). Bucket expected probability uses the actual mean quotes, not the midpoint of the bucket. Wilson intervals use z = 1.96. Empty samples yield null/“—”, not zero performance.

## Chronological split

Normalize timestamps to UTC, choose the earliest observation per ticker, sort by timestamp then ticker. The boundary is the decision at floor(0.7 × canonical count), with a floating-point tolerance. Keep equal timestamps on the same side of the boundary. Research observations whose labels are not settled strictly before the boundary are purged. The resulting counts need not be exactly 70/30 when there are ties or purges. Test rows can be related economically even if ticker identifiers differ.

The importer checks settlement identity across all observations of a ticker. It cannot independently authenticate official settlement values; that is a source verification requirement.

## Expanding windows

Divide canonical rows into five consecutive chunks. For each of four later chunks, use earlier rows as a diagnostic research window and that chunk as evaluation. Purge research labels not available before its test window. No model is trained or fitted. This is temporal reporting, not a claim of walk-forward-optimized performance. Final remainder rows belong to the final fold.

## Bootstrap

Sort test markets chronologically. Draw contiguous overlapping blocks with replacement, concatenate until sample length is reached, and trim to original length. Repeat 1,000 times with seed 27. Report empirical 2.5% and 97.5% quantiles of the mean using floor-indexed order statistics. Default block length is min(12, n). This estimates conditional uncertainty under this resampling model; it does not correct multiple testing, guarantee dependence capture, or imply future profitability.

## Feature inspection

Eight feature names are allowlisted. Numeric bucket boundaries are preset, not optimized from outcomes. Research and later-test means are reported separately. Fewer than 30 markets in either period yields “Needs more data.” Opposing mean-return signs yield “Direction changed.” Matching signs yield “Same direction · unconfirmed.” None is a statistically validated promotion or rejection decision. Pairwise searches increase false-discovery risk. Outcomes are allowed as retrospective labels in tables, never as predictor inputs.

## Execution scenarios

Let q be side price, y selected-side payoff, s slippage in dollars, f fee in dollars and r assumed fill probability. Expected contribution per attempted contract is r(y−q−s−f) when q+s<1, otherwise zero. Gross results include all attempts before eligibility/cost adjustments. Fees apply to expected fills only. Fill probability is independent of outcome. No latency, queue, path, partial-fill sequence or adverse-selection model is implemented. Fill-rate fractions are expectations, not fractional historical trade counts.

## Public sampling

The SQLite exporter chooses the earliest observation per ticker, sorts chronologically, and selects evenly spaced index positions up to the requested limit, including both endpoints. This controls size and retains date coverage but can alias periodic patterns. Use full data for substantive inference; the browser sample is for product inspection and descriptive work. Maximum browser input is 10,000 observations / 25 MB.

## Reconciliation

Fictional records exercise five checks: matched, mismatch, awaiting official settlement, missing local settlement, and duplicate event. This is a status classifier, not an append-only event-sourcing system, execution attribution service or settlement API integration.

## Provenance

The build reconstructs a safe metadata dictionary and normalizes every public row. Arbitrary top-level metadata is discarded. The displayed dataset SHA-256 is computed from the exact downloadable sanitized public-input JSON. Source-file hashes identify imported archives separately. Hashes provide identity, not independent verification of factual accuracy.
