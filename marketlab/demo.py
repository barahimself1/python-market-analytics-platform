"""Deterministic fictional fixture. No KLEM outcomes or private rules are used."""
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import random
from .schema import normalize


def generate(destination: Path, n: int = 720) -> None:
    rng = random.Random(20261026)
    start = datetime(2026,5,1,tzinfo=timezone.utc)
    rows = []
    for i in range(n):
        when = start+timedelta(hours=4*i)
        p = round(rng.uniform(.08,.94),4)
        ttx = rng.choice([2,5,8,12])
        # Deliberate illustrative temporal shift, not estimated market behavior.
        probability = min(.98,max(.02,p+(.035 if i < .7*n else -.025)))
        rows.append(normalize({'ticker': f'DEMO-BTC-{i+1:05d}', 'timestamp': when.isoformat(),
          'settlement_time': (when+timedelta(minutes=ttx)).isoformat(), 'probability':p,
          'outcome':int(rng.random()<probability),'side':rng.choice(['YES','NO']),
          'ttx_minutes':ttx, 'atr':round(rng.uniform(25,250),2),
          'normalized_distance':round(rng.uniform(-2.5,2.5),3), 'momentum':round(rng.gauss(0,.7),3)}))
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps({'schema_version':1,'kind':'synthetic',
      'label':'Synthetic demonstration', 'sampling':'Seeded fictional markets, one observation per ticker; no real KLEM results.',
      'seed':20261026,'rows':rows},indent=2)+'\n')
