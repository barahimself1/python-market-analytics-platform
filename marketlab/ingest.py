"""Streaming ingestion into disk-backed SQLite. Raw records are never copied."""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
from .schema import normalize

MAX_LINE = 2_000_000


def records(path: Path):
    """Bounded JSONL reader; CSV field sizes are bounded by the csv module."""
    with path.open(encoding='utf-8-sig', newline='') as handle:
        if path.suffix.lower() == '.csv':
            yield from enumerate(csv.DictReader(handle),1)
        elif path.suffix.lower() == '.jsonl':
            index = 0
            while True:
                line = handle.readline(MAX_LINE+1)
                if not line:
                    break
                index += 1
                if len(line) > MAX_LINE:
                    raise ValueError('JSONL record exceeds 2 MB; use flat records')
                if not line.strip():
                    continue
                try:
                    yield index, json.loads(line)
                except json.JSONDecodeError:
                    yield index, None
        else:
            raise ValueError('input must be CSV or JSONL')


def ingest(path: Path, database: Path, mapping: dict | None = None) -> dict:
    """Use explicit field mappings, allowlisted output, transactional dedup.
    One row per (ticker, timestamp); conflicting duplicates are rejected.
    Reports contain only row numbers and generic errors, never source values.
    """
    database.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            digest.update(chunk)
    report = {'source_sha256': digest.hexdigest(), 'accepted': 0, 'duplicates': 0, 'rejected': 0, 'errors': []}
    with sqlite3.connect(database) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS observations (ticker TEXT, timestamp TEXT, payload TEXT, PRIMARY KEY(ticker,timestamp))')
        for index, raw in records(path):
            try:
                if not isinstance(raw,dict):
                    raise ValueError('malformed record')
                row = normalize(raw,mapping)
                previous = connection.execute('SELECT payload FROM observations WHERE ticker=? LIMIT 1',(row['ticker'],)).fetchone()
                if previous:
                    prior = json.loads(previous[0])
                    if (prior['outcome'],prior['settlement_time']) != (row['outcome'],row['settlement_time']):
                        raise ValueError('conflicting ticker settlement identity')
                payload = json.dumps(row,sort_keys=True)
                existing = connection.execute('SELECT payload FROM observations WHERE ticker=? AND timestamp=?',(row['ticker'],row['timestamp'])).fetchone()
                if existing:
                    if existing[0] != payload:
                        raise ValueError('conflicting duplicate observation')
                    report['duplicates'] += 1
                else:
                    connection.execute('INSERT INTO observations VALUES (?,?,?)',(row['ticker'],row['timestamp'],payload))
                    report['accepted'] += 1
            except (ValueError,TypeError,KeyError):
                report['rejected'] += 1
                if len(report['errors']) < 20:
                    report['errors'].append({'row': index, 'reason': 'Invalid or conflicting record; inspect locally'})
        connection.execute('CREATE TABLE IF NOT EXISTS sources (sha256 TEXT PRIMARY KEY, report TEXT)')
        connection.execute('INSERT OR REPLACE INTO sources VALUES (?,?)',(report['source_sha256'],json.dumps(report)))
    return report


def export(database: Path, destination: Path, limit: int = 5000) -> dict:
    """Deterministic evenly spaced ticker sample, preserving chronological span.
    SQLite handles grouping on disk; Python holds at most `limit` observations.
    Earliest observation per ticker is the canonical sampling unit. Never label
    a sample's metrics as full archive metrics.
    """
    if not 2 <= limit <= 10000:
        raise ValueError('public export limit must be 2..10000 markets')
    with sqlite3.connect(database) as connection:
        total = connection.execute('SELECT COUNT(DISTINCT ticker) FROM observations').fetchone()[0]
        if total < 2:
            raise ValueError('at least two valid tickers required')
        count = min(total,limit)
        indices = {round(i*(total-1)/(count-1)) for i in range(count)}
        query = '''SELECT o.payload FROM observations o JOIN
                   (SELECT ticker, MIN(timestamp) timestamp FROM observations GROUP BY ticker) c
                   ON o.ticker=c.ticker AND o.timestamp=c.timestamp ORDER BY o.timestamp,o.ticker'''
        rows = [json.loads(payload) for index,(payload,) in enumerate(connection.execute(query)) if index in indices]
        hashes = [r[0] for r in connection.execute('SELECT sha256 FROM sources ORDER BY sha256')]
    payload = {'schema_version': 1, 'kind': 'imported', 'label': 'Imported public sample',
               'sampling': 'Evenly spaced canonical tickers across full time coverage; descriptive sample, not full-universe inference.',
               'source_tickers': total, 'source_sha256': hashes, 'rows': rows}
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(payload,indent=2)+'\n')
    return {'exported':len(rows),'source_tickers':total}
