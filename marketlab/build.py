"""Compile verified public input into an offline-capable static research app."""
import hashlib
import json
from pathlib import Path
import shutil
from .analytics import summary, calibration, chronological_split, block_bootstrap, walk_forward, reconcile
from .schema import normalize

ROOT = Path(__file__).resolve().parents[1]


def build(source: Path, destination: Path) -> dict:
    if source.stat().st_size > 25_000_000:
        raise ValueError('public input exceeds 25 MB; export a smaller sample')
    dataset = json.loads(source.read_text())
    if dataset.get('schema_version') != 1 or dataset.get('kind') not in ('synthetic','imported'):
        raise ValueError('invalid dataset metadata')
    rows = [normalize(r) for r in dataset['rows']]
    # Reconstruct public metadata rather than copying arbitrary source fields.
    safe = {'schema_version': 1, 'kind': dataset['kind'],
            'label': 'Synthetic demonstration' if dataset['kind']=='synthetic' else 'Imported public sample',
            'sampling': 'Seeded fictional markets; no real KLEM results.' if dataset['kind']=='synthetic' else
                        'Public canonical sample; descriptive analysis, not full-universe inference.',
            'rows': rows}
    if dataset['kind']=='synthetic' and isinstance(dataset.get('seed'), int):
        safe['seed'] = dataset['seed']
    if dataset['kind']=='imported':
        if isinstance(dataset.get('source_tickers'), int) and dataset['source_tickers'] >= len(rows):
            safe['source_tickers'] = dataset['source_tickers']
        import re
        hashes = dataset.get('source_sha256', [])
        if isinstance(hashes, list) and all(isinstance(h,str) and re.fullmatch(r'[a-f0-9]{64}',h) for h in hashes):
            safe['source_sha256'] = hashes
    dataset = safe
    if not rows or len(rows)>10000:
        raise ValueError('public application requires 1..10000 observations')
    identities = {}
    observations = {}
    for row in rows:
        key = (row['ticker'], row['timestamp'])
        if key in observations and observations[key] != row:
            raise ValueError('conflicting duplicate public observation')
        observations[key] = row
        identity = (row['settlement_time'], row['outcome'])
        if row['ticker'] in identities and identities[row['ticker']] != identity:
            raise ValueError('conflicting settlement identity for one ticker')
        identities[row['ticker']] = identity
    split = chronological_split(rows)
    canonical = split['research']+split['test']
    for period in ('research','test'):
        for row in split[period]:
            row['period'] = period
    reconciliation = reconcile([
      {'event_id': 'SIM-001','ticker':'DEMO-SETTLEMENT-001','recorded_outcome':1,'official_outcome':1},
      {'event_id': 'SIM-002','ticker':'DEMO-SETTLEMENT-002','recorded_outcome':0,'official_outcome':1},
      {'event_id': 'SIM-003','ticker':'DEMO-SETTLEMENT-003','recorded_outcome':None,'official_outcome':0},
      {'event_id': 'SIM-004','ticker':'DEMO-SETTLEMENT-004','recorded_outcome':1,'official_outcome':None},
      {'event_id': 'SIM-001','ticker':'DEMO-SETTLEMENT-001','recorded_outcome':1,'official_outcome':1}])
    public_text = json.dumps({**dataset, 'rows': [normalize(r) for r in rows]}, indent=2)+'\n'
    result = {**{k:v for k,v in dataset.items() if k!='rows'}, 'rows':canonical,
      'dataset_sha256': hashlib.sha256(public_text.encode()).hexdigest(),
      'summary':summary(canonical), 'periods':{p:summary(split[p]) for p in ('research','test')},
      'calibration':{p:calibration(split[p]) for p in ('research','test')},
      'validation':{'cutoff':split['cutoff'],'purged':len(split['purged']),
        'bootstrap':block_bootstrap(split['test'],min(12,len(split['test']))) if split['test'] else {'ci':None,'n':0},
        'folds':walk_forward(canonical)}, 'reconciliation':reconciliation,
      'claims':json.loads((ROOT/'research/claims.json').read_text())}
    destination.mkdir(parents=True,exist_ok=True)
    for path in (ROOT/'web').iterdir():
        if path.is_file():
            shutil.copy2(path,destination/path.name)
    # JSON escaped before embedding in JS; no source string can close a script.
    (destination/'dataset.js').write_text('window.MARKETLAB_DATA = '+json.dumps(result,ensure_ascii=True).replace('<','\\u003c')+';\n')
    (destination/'public-dataset.json').write_text(public_text)
    (destination/'.nojekyll').write_text('')
    return {'markets':len(canonical),'kind':dataset['kind'],'purged':len(split['purged'])}
