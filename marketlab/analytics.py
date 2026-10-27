"""Auditable analytical primitives; returns are dollars per $1 contract."""
from collections import defaultdict
import math
import random
from statistics import mean, median
from .schema import trade_values, utc


def wilson(wins: int, count: int, z: float = 1.96) -> list[float] | None:
    """95% Wilson score interval for a binomial rate; empty samples are null."""
    if count == 0:
        return None
    if not 0 <= wins <= count:
        raise ValueError('wins must be within sample count')
    p = wins/count
    center = (p+z*z/(2*count))/(1+z*z/count)
    half = z*math.sqrt(p*(1-p)/count+z*z/(4*count*count))/(1+z*z/count)
    return [max(0,center-half), min(1,center+half)]


def summary(rows: list[dict]) -> dict:
    if not rows:
        return {'n': 0, 'win_rate': None, 'mean_return': None, 'median_return': None, 'brier': None, 'ci': None}
    trades = [trade_values(r) for r in rows]
    returns = [win-price for price, win in trades]
    wins = sum(win for _, win in trades)
    return {'n': len(rows), 'win_rate': wins/len(rows), 'mean_return': mean(returns),
            'median_return': median(returns), 'brier': mean((r['probability']-r['outcome'])**2 for r in rows),
            'ci': wilson(wins, len(rows))}


def chronological_split(rows: list[dict], fraction: float = .7) -> dict:
    """One canonical observation per ticker; purge labels unavailable at cutoff.

    Keep the earliest observation for each ticker. Cut only between distinct
    timestamps. Purge research rows whose settlement is not before the first
    test decision, preventing labels crossing the research/test boundary.
    """
    if not 0 < fraction < 1:
        raise ValueError('split fraction must be between 0 and 1')
    groups = {}
    for row in sorted(rows, key=lambda r: (r['timestamp'], r['ticker'])):
        groups.setdefault(row['ticker'], row)
    ordered = list(groups.values())
    if len(ordered) < 2:
        return {'research': [], 'test': ordered, 'purged': [], 'cutoff': None}
    boundary = ordered[min(len(ordered)-1, max(1, math.floor(len(ordered)*fraction + 1e-9)))]['timestamp']
    research, test, purged = [], [], []
    for row in ordered:
        if row['timestamp'] >= boundary:
            test.append(row)
        elif row['settlement_time'] >= boundary:
            purged.append(row)
        else:
            research.append(row)
    return {'research': research, 'test': test, 'purged': purged, 'cutoff': boundary}


def calibration(rows: list[dict], bins: int = 10) -> list[dict]:
    if bins < 2:
        raise ValueError('at least two bins required')
    groups = defaultdict(list)
    for row in rows:
        groups[min(bins-1,int(row['probability']*bins))].append(row)
    return [{'bucket': bucket, 'low': bucket/bins, 'high': (bucket+1)/bins,
             'n': len(group), 'expected': mean(r['probability'] for r in group),
             'observed': mean(r['outcome'] for r in group),
             'ci': wilson(sum(r['outcome'] for r in group), len(group))}
            for bucket, group in sorted(groups.items())]


def block_bootstrap(rows: list[dict], block_size: int = 12, repetitions: int = 1000, seed: int = 27) -> dict:
    """Moving-block bootstrap of chronological per-market returns, conditional
    on this sample and these assumptions; not adjusted for strategy search.
    """
    values = [trade_values(r)[1]-trade_values(r)[0] for r in sorted(rows,key=lambda r:r['timestamp'])]
    n = len(values)
    if not values:
        return {'ci': None, 'n': 0, 'block_size': block_size, 'repetitions': repetitions}
    if not 1 <= block_size <= n or repetitions < 100:
        raise ValueError('invalid block size or repetitions')
    rng = random.Random(seed)
    estimates = []
    for _ in range(repetitions):
        sample = []
        while len(sample) < n:
            start = rng.randrange(n-block_size+1)
            sample.extend(values[start:start+block_size])
        estimates.append(mean(sample[:n]))
    estimates.sort()
    return {'ci': [estimates[int(.025*(repetitions-1))], estimates[int(.975*(repetitions-1))]],
            'n': n, 'block_size': block_size, 'repetitions': repetitions, 'seed': seed}


def walk_forward(rows: list[dict], folds: int = 4) -> list[dict]:
    """Expanding chronological windows; descriptive evaluation, no fitting."""
    ordered = sorted(rows, key=lambda r:r['timestamp'])
    size = len(ordered)//(folds+1)
    if size < 2:
        return []
    result = []
    for index in range(1,folds+1):
        test = ordered[index*size:(index+1)*size if index<folds else len(ordered)]
        train = [r for r in ordered[:index*size] if r['settlement_time'] < test[0]['timestamp']]
        result.append({'fold': index, 'research': summary(train), 'test': summary(test),
                       'start': test[0]['timestamp'], 'end': test[-1]['timestamp']})
    return result


def execution(rows: list[dict], fee_cents: float = 1, slippage_cents: float = 1, fill_rate: float = .9) -> dict:
    """Expected net $ / attempted contract, under uniform independent fills.
    This is a cost scenario, not a historical fill or latency simulator.
    """
    if fee_cents < 0 or slippage_cents < 0 or not 0 <= fill_rate <= 1:
        raise ValueError('invalid execution assumptions')
    eligible = [r for r in rows if trade_values(r)[0]+slippage_cents/100 < 1]
    gross = sum(trade_values(r)[1]-trade_values(r)[0] for r in rows)
    net = sum(trade_values(r)[1]-trade_values(r)[0]-(fee_cents+slippage_cents)/100 for r in eligible)*fill_rate
    return {'attempts': len(rows), 'eligible': len(eligible), 'gross': gross, 'net': net,
            'expected_fills': len(eligible)*fill_rate, 'mean_net': net/len(rows) if rows else None}


def reconcile(records: list[dict]) -> list[dict]:
    """Compare recorded YES settlement with official YES settlement."""
    seen = set()
    result = []
    for record in records:
        event = record['event_id']
        duplicate = event in seen
        seen.add(event)
        local, official = record.get('recorded_outcome'), record.get('official_outcome')
        if duplicate:
            status = 'Duplicate event'
        elif official not in (0,1):
            status = 'Awaiting official settlement'
        elif local not in (0,1):
            status = 'Missing local settlement'
        elif local != official:
            status = 'Mismatch'
        else:
            status = 'Matched'
        result.append({**record, 'status': status})
    return result
