import copy,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from wdfg.validation import ROOT,Invalid,read_json,validate,verify_package
ROOT = Path(__file__).resolve().parents[1]
PACK=ROOT/'protocol'

class ValidationTests(unittest.TestCase):
 def setUp(self): self.c=read_json(ROOT/'configs/fixture-p1.json')
 def test_baseline(self):
  r=validate(self.c,PACK);self.assertEqual(r['validated_payload_files'],len(read_json(PACK/'manifest.json')['files']));self.assertFalse(r['execution_authorized']);self.assertEqual(r['scientific_status'],'NOT_EVALUATED')
 def test_canonical_digest(self):
  r=validate(self.c,PACK);self.assertEqual(r['config_sha256'],validate(dict(reversed(list(self.c.items()))),PACK)['config_sha256']);self.c['seed']+=1;self.assertNotEqual(r['config_sha256'],validate(self.c,PACK)['config_sha256'])
 def test_required_fields(self):
  for k in ['seed','model_revision','source_commit','dataset_sha256']:
   c=copy.deepcopy(self.c);del c[k]
   with self.assertRaises(Invalid):validate(c,PACK)
 def test_invalid_scientific_values(self):
  for v in [None,True,'0.001',0.01]:
   self.c['scientific_parameters']['coefficient_threshold']=v
   with self.assertRaises(Invalid):validate(self.c,PACK)
 def test_no_empirical_escalation(self):
  for kind in ['pilot','result']:
   for data in ['synthetic','empirical']:
    c=copy.deepcopy(self.c);c.update(run_kind=kind,data_kind=data,freeze_status='frozen',open_freezes=[])
    with self.assertRaises(Invalid):validate(c,PACK)
 def test_freeze_contradiction(self):
  self.c['freeze_status']='frozen'
  with self.assertRaises(Invalid):validate(self.c,PACK)
 def test_protocol_mismatch(self):
  self.c['protocol_sha256']='0'*64
  with self.assertRaises(Invalid):validate(self.c,PACK)
 def test_i0b_and_missing_k(self):
  self.c['stage']='P3';self.c['scientific_parameters']=dict(K=8,B=32,regime='I0b',decoding={'temperature':0},precision_receipt_sha256='fixture-only')
  self.assertEqual(validate(self.c,PACK)['scientific_status'],'NOT_EVALUATED');self.c['scientific_parameters']['K']=None
  with self.assertRaises(Invalid):validate(self.c,PACK)
 def test_tampering(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'pack';shutil.copytree(PACK,p);f=p/'README.md';old=f.read_bytes();f.write_bytes(old+b'changed')
   with self.assertRaises(Invalid):verify_package(p)
   f.write_bytes(old);(p/'extra').write_text('extra')
   with self.assertRaises(Invalid):verify_package(p)
 def test_manifest_rewrite(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'pack';shutil.copytree(PACK,p);m=read_json(p/'manifest.json');m['files']=[];(p/'manifest.json').write_text(json.dumps(m))
   with self.assertRaises(Invalid):verify_package(p)
 def test_duplicate_json(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x';p.write_text('{"seed":42,"seed":43}')
   with self.assertRaises(Invalid):read_json(p)
 def test_cli_error(self):
  r=subprocess.run([sys.executable,'-m','wdfg','validate-config','/nonexistent/wdfg.json','--package',str(PACK)],cwd=ROOT,capture_output=True,text=True)
  self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stderr)['validation_status'],'FAIL')
