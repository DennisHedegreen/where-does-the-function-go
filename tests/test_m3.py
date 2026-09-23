import copy,unittest
from wdfg.validation import ROOT,Invalid,read_json
from wdfg.m3 import audit_backup
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class M3Tests(unittest.TestCase):
 def setUp(self):self.e=read_json(ROOT/'fixtures/backup-near-null.json')
 def row(self):return self.e['pools'][0]['candidates'][0]
 def test_near_null_not_reconstitution(self):
  r=audit_backup(self.e);self.assertEqual(r['fixture_backup_state'],'B0-A');self.assertFalse(r['fixture_strong_label_available']);self.assertEqual(r['scientific_status'],'NOT_EVALUATED')
 def test_all_gates_needed(self):
  self.e['reconstitution_gates']={k:'PASS' for k in self.e['reconstitution_gates']};self.assertTrue(audit_backup(self.e)['fixture_strong_label_available'])
  for k in self.e['reconstitution_gates']:
   e=copy.deepcopy(self.e);e['reconstitution_gates'][k]='UNRESOLVED';self.assertFalse(audit_backup(e)['fixture_strong_label_available'])
 def test_low_power(self):
  self.row()['power']['value']=.79999;self.assertEqual(audit_backup(self.e)['fixture_backup_state'],'UNRESOLVED')
 def test_ci_touches_margin(self):
  self.row()['ci']['high']=.01;self.assertEqual(audit_backup(self.e)['fixture_backup_state'],'UNRESOLVED')
 def test_expansion_disagreement(self):
  self.e['pools'][1]['candidates'][1]['ci']['low']=-.02;self.assertEqual(audit_backup(self.e)['fixture_backup_state'],'UNRESOLVED')
 def test_reference_missing(self):
  self.e['coax_reference']['status']='UNRESOLVED';self.assertEqual(audit_backup(self.e)['fixture_backup_state'],'UNRESOLVED')
 def test_t0_changed(self):
  self.e['t0']['lineage']['mask_sha256']='d'*64
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_design_changed(self):
  self.e['design']['pool_selection_rule']='changed'
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_power_wrong_n(self):
  self.row()['power']['n']=999
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_pairing_required(self):
  self.e['design']['effect_method']='unpaired'
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_missing_pool_candidate(self):
  self.e['pools'][1]['candidates'].pop()
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_invalid_count(self):
  self.row()['paired_counts']['00']=True
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_empirical_refused(self):
  self.e['run_kind']='result'
  with self.assertRaises(Invalid):audit_backup(self.e)
 def test_m2_t0_roundtrip(self):
  import tempfile,json
  from pathlib import Path
  from wdfg.m2 import write_t0,verify_t0
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'t0.json';t=self.e['t0']
   digest=write_t0(p,records=t['records'],lineage=t['lineage'])
   self.assertEqual(digest,self.e['expected_t0_sha256'])
   self.e['t0']=verify_t0(p,digest)
   self.assertEqual(audit_backup(self.e)['fixture_backup_state'],'B0-A')
