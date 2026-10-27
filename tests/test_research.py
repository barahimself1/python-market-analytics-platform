"""Regression tests of analysis, temporal boundaries, import and public output."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from marketlab.schema import normalize,trade_values,FEATURES
from marketlab.analytics import summary,wilson,calibration,chronological_split,block_bootstrap,execution,reconcile,walk_forward
from marketlab.ingest import ingest,export,records
from marketlab.build import build
from marketlab.demo import generate


def row(i=0,**kwargs):
    date=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(hours=i)
    data={'ticker':f'TEST-{i}','timestamp':date.isoformat(),'settlement_time':(date+timedelta(minutes=10)).isoformat(),
          'probability':.8,'outcome':1,'side':'YES','ttx_minutes':10,'atr':50,'normalized_distance':.5,'momentum':.1}
    data.update(kwargs)
    return normalize(data)


class AnalyticsTests(unittest.TestCase):
    def test_yes_and_no_contract_returns(self):
        self.assertEqual(trade_values(row()),(.8,1))
        cost,win=trade_values(row(side='NO'))
        self.assertAlmostEqual(cost,.2)
        self.assertEqual(win,0)
    def test_hand_computed_summary(self):
        s=summary([row(),row(1,outcome=0,probability=.2)])
        self.assertAlmostEqual(s['mean_return'],0)
        self.assertAlmostEqual(s['brier'],.04)
        self.assertEqual(s['win_rate'],.5)
    def test_empty_is_not_zero_performance(self):
        self.assertIsNone(summary([])['mean_return'])
        self.assertIsNone(wilson(0,0))
    def test_wilson_known_half_sample(self):
        lo,hi=wilson(50,100)
        self.assertAlmostEqual(lo,.40383,places=4)
        self.assertAlmostEqual(hi,.59617,places=4)
    def test_wilson_zero_wins_not_zero_uncertainty(self):
        self.assertGreater(wilson(0,10)[1],.2)
    def test_bucket_mean_uses_actual_quotes(self):
        data=calibration([row(probability=.81),row(1,probability=.89)])
        self.assertEqual(data[0]['n'],2)
        self.assertAlmostEqual(data[0]['expected'],.85)
    def test_split_exact_seventy_percent(self):
        s=chronological_split([row(i) for i in range(720)])
        self.assertEqual(len(s['research']),504)
        self.assertEqual(len(s['test']),216)
    def test_tickers_never_cross_split(self):
        rs=[row(i) for i in range(10)]
        rs.append({**rs[0],'timestamp':rs[-1]['timestamp']})
        s=chronological_split(rs)
        self.assertFalse({r['ticker'] for r in s['research']}&{r['ticker'] for r in s['test']})
        self.assertEqual(sum(map(len,[s['research'],s['test'],s['purged']])),10)
    def test_unsettled_labels_are_purged(self):
        rs=[row(i) for i in range(10)]
        rs[0]['settlement_time']=rs[8]['settlement_time']
        s=chronological_split(rs)
        self.assertEqual([r['ticker'] for r in s['purged']],['TEST-0'])
    def test_equal_decision_times_not_split(self):
        rs=[row(i) for i in range(10)]
        rs[6]['timestamp']=rs[7]['timestamp']
        s=chronological_split(rs)
        self.assertNotIn('TEST-6',{r['ticker'] for r in s['research']})
    def test_bootstrap_constant_known_result(self):
        v=block_bootstrap([row(i) for i in range(25)],5,100)
        for bound in v['ci']:
            self.assertAlmostEqual(bound,.2)
    def test_bootstrap_is_seeded(self):
        rs=[row(i,outcome=i%2) for i in range(25)]
        self.assertEqual(block_bootstrap(rs,4,100),block_bootstrap(rs,4,100))
    def test_zero_fills_zero_expected_net(self):
        self.assertEqual(execution([row()],1,1,0)['net'],0)
    def test_cost_scenario_known_result(self):
        v=execution([row()],1,2,.5)
        self.assertAlmostEqual(v['net'],.085)
        self.assertEqual(v['expected_fills'],.5)
    def test_impossible_entry_rejected(self):
        self.assertEqual(execution([row(probability=.99)],0,2,1)['eligible'],0)
    def test_reconciliation_exceptions(self):
        fixtures=[{'event_id':'a','recorded_outcome':1,'official_outcome':1},
          {'event_id':'a','recorded_outcome':1,'official_outcome':1},
          {'event_id':'b','recorded_outcome':0,'official_outcome':1},
          {'event_id':'c','recorded_outcome':1,'official_outcome':None},
          {'event_id':'d','recorded_outcome':None,'official_outcome':0}]
        self.assertEqual([r['status'] for r in reconcile(fixtures)],['Matched','Duplicate event','Mismatch','Awaiting official settlement','Missing local settlement'])
    def test_walk_forward_has_later_windows(self):
        folds=walk_forward([row(i) for i in range(50)])
        self.assertEqual([f['research']['n'] for f in folds],[10,20,30,40])
        self.assertEqual([f['test']['n'] for f in folds],[10]*4)
    def test_leaky_feature_not_allowed(self):
        self.assertFalse({'outcome','edge_vs_implied','return','settlement_time'}&set(FEATURES))


class SchemaTests(unittest.TestCase):
    def test_unknown_private_fields_dropped(self):
        self.assertNotIn('account_id',normalize({**row(),'account_id':'private-example'}))
    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError): row(timestamp='2026-01-01T00:00:00')
    def test_percent_units_rejected(self):
        with self.assertRaises(ValueError): row(probability=80)
    def test_nonfinite_rejected(self):
        for field in ['probability','atr','momentum','ttx_minutes']:
            with self.subTest(field=field),self.assertRaises(ValueError):row(**{field:float('nan')})
    def test_post_settlement_observation_rejected(self):
        with self.assertRaises(ValueError):row(settlement_time='2025-12-31T00:00:00+00:00')
    def test_mismatched_ttx_rejected(self):
        with self.assertRaises(ValueError):row(ttx_minutes=90)
    def test_invalid_ticker_rejected(self):
        with self.assertRaises(ValueError):row(ticker='<script>bad</script>')
    def test_calendar_features_derived(self):
        self.assertEqual(row(session='Fake',weekday='Fake')['session'],'Asia')
        self.assertEqual(row(weekday='Fake')['weekday'],'Thu')


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def source(self,values):
        path=self.root/'input.jsonl'
        path.write_text('\n'.join(json.dumps(v) for v in values)+'\n')
        return path
    def test_ingestion_dedup_and_invalid_rows(self):
        p=self.source([row(),row(),{'bad':True}]);db=self.root/'private.sqlite'
        result=ingest(p,db)
        self.assertEqual((result['accepted'],result['duplicates'],result['rejected']),(1,1,1))
    def test_conflicting_duplicate_rejected(self):
        result=ingest(self.source([row(),row(probability=.7)]),self.root/'db.sqlite')
        self.assertEqual(result['rejected'],1)
    def test_conflicting_settlement_rejected(self):
        result=ingest(self.source([row(),row(1,ticker='TEST-0',outcome=0)]),self.root/'db.sqlite')
        self.assertEqual(result['rejected'],1)
    def test_malformed_json_counted(self):
        p=self.source([row()]);p.write_text(p.read_text()+'not json\n')
        self.assertEqual(ingest(p,self.root/'db.sqlite')['rejected'],1)
    def test_mapping_does_not_infer_units(self):
        r=row();r['yes_quote']=r.pop('probability')
        self.assertEqual(ingest(self.source([r]),self.root/'db.sqlite',{'probability':'yes_quote'})['accepted'],1)
    def test_export_limit_and_time_coverage(self):
        db=self.root/'db.sqlite';ingest(self.source([row(i) for i in range(20)]),db)
        out=self.root/'public.json';export(db,out,5);data=json.loads(out.read_text())
        self.assertEqual(len(data['rows']),5)
        self.assertEqual(data['rows'][0]['ticker'],'TEST-0')
        self.assertEqual(data['rows'][-1]['ticker'],'TEST-19')
        self.assertEqual(data['kind'],'imported')
    def test_private_fields_absent_from_database(self):
        db=self.root/'db.sqlite';ingest(self.source([{**row(),'account_id':'PRIVATE_MARKER'}]),db)
        with sqlite3.connect(db) as c:
            self.assertNotIn('PRIVATE_MARKER',c.execute('SELECT payload FROM observations').fetchone()[0])
    def test_build_strips_unknown_metadata(self):
        p=self.root/'demo.json';generate(p,30);data=json.loads(p.read_text());data['private_token']='PRIVATE_MARKER';data['rows'][0]['private_note']='PRIVATE_MARKER';p.write_text(json.dumps(data))
        dest=self.root/'dist';build(p,dest)
        for file in ['dataset.js','public-dataset.json']:
            self.assertNotIn('PRIVATE_MARKER',(dest/file).read_text())
    def test_build_is_reproducible(self):
        p=self.root/'demo.json';generate(p,30)
        build(p,self.root/'one');build(p,self.root/'two')
        self.assertEqual((self.root/'one/dataset.js').read_bytes(),(self.root/'two/dataset.js').read_bytes())
    def test_demo_generation_reproducible(self):
        a,b=self.root/'a.json',self.root/'b.json';generate(a,20);generate(b,20)
        self.assertEqual(a.read_bytes(),b.read_bytes())
    def test_public_hash_matches_downloadable_input(self):
        import hashlib
        p=self.root/'demo.json';generate(p,30);dest=self.root/'dist';build(p,dest)
        compiled=json.loads((dest/'dataset.js').read_text().removeprefix('window.MARKETLAB_DATA = ').removesuffix(';\n'))
        self.assertEqual(compiled['dataset_sha256'],hashlib.sha256((dest/'public-dataset.json').read_bytes()).hexdigest())
    def test_csv_import(self):
        import csv
        p=self.root/'input.csv'
        with p.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(row()));writer.writeheader();writer.writerow(row())
        self.assertEqual(ingest(p,self.root/'db.sqlite')['accepted'],1)
    def test_direct_build_conflicting_duplicate_rejected(self):
        p=self.root/'bad.json';p.write_text(json.dumps({'schema_version':1,'kind':'imported','rows':[row(),row(probability=.7)]}))
        with self.assertRaises(ValueError):build(p,self.root/'dist')
    def test_imported_pipeline_retains_evidence_type(self):
        db=self.root/'db.sqlite';ingest(self.source([row(i) for i in range(20)]),db)
        p=self.root/'public.json';export(db,p,10)
        self.assertEqual(build(p,self.root/'dist')['kind'],'imported')
    def test_no_input_required_for_demo(self):
        p=self.root/'demo.json';generate(p,30);result=build(p,self.root/'dist')
        self.assertEqual(result['kind'],'synthetic')
        self.assertTrue((self.root/'dist/index.html').exists())

if __name__=='__main__':unittest.main()
