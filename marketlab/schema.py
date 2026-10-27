"""Strict public schema. Only explicit decision-time fields cross the boundary."""
from datetime import datetime, timezone
import math
import re

FEATURES = ('probability', 'ttx_minutes', 'atr', 'normalized_distance', 'momentum', 'session', 'side', 'weekday')
FIELDS = ('ticker', 'timestamp', 'settlement_time', 'probability', 'outcome', 'side', 'ttx_minutes', 'atr', 'normalized_distance', 'momentum', 'session', 'weekday')


def utc(value: str) -> datetime:
    """Reject naive timestamps instead of silently assigning a time zone."""
    date = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('timestamp requires an explicit timezone')
    return date.astimezone(timezone.utc)


def normalize(raw: dict, mapping: dict | None = None) -> dict:
    """Normalize one YES-probability observation. No unit or side inference.

    Probability is always YES probability in [0,1]; outcome is official YES
    settlement (0 or 1), even when side=NO. Mapping: canonical -> source field.
    Unknown fields, including account data, never enter the output.
    """
    mapping = mapping or {}
    row = {field: raw.get(mapping.get(field, field)) for field in FIELDS}
    ticker = str(row['ticker'] or '')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', ticker):
        raise ValueError('invalid ticker')
    row['ticker'] = ticker
    start, end = utc(row['timestamp']), utc(row['settlement_time'])
    if end <= start:
        raise ValueError('settlement must follow observation')
    row['timestamp'], row['settlement_time'] = start.isoformat(), end.isoformat()
    for field in ('probability', 'ttx_minutes', 'atr', 'normalized_distance', 'momentum'):
        value = float(row[field])
        if not math.isfinite(value):
            raise ValueError(f'{field} must be finite')
        row[field] = value
    if not 0 < row['probability'] < 1:
        raise ValueError('probability must be a fraction strictly between 0 and 1')
    if row['ttx_minutes'] <= 0 or row['atr'] < 0:
        raise ValueError('invalid TTX or ATR')
    if abs(row['ttx_minutes'] - (end-start).total_seconds()/60) > 1:
        raise ValueError('TTX differs from settlement time by more than one minute')
    if str(row['outcome']) not in ('0', '1', '0.0', '1.0'):
        raise ValueError('outcome must be official YES result, 0 or 1')
    row['outcome'] = int(float(row['outcome']))
    row['side'] = str(row['side']).upper()
    if row['side'] not in ('YES', 'NO'):
        raise ValueError('side must be YES or NO')
    # Session and weekday are derived from decision time, never trusted from source.
    row['session'] = 'Asia' if start.hour < 8 else 'Europe' if start.hour < 16 else 'Americas'
    row['weekday'] = start.strftime('%a')
    return row


def trade_values(row: dict) -> tuple[float, int]:
    """Entry cost and win indicator for the selected side, per $1 contract."""
    return (row['probability'], row['outcome']) if row['side'] == 'YES' else (1-row['probability'], 1-row['outcome'])
