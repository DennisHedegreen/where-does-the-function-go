import copy,json,tempfile,unittest
from pathlib import Path
import torch
from torch import nn
from wdfg.m2 import PersistentMask,write_t0,verify_t0
from wdfg.validation import Invalid

class MLP(nn.Module):
 def __init__(self):
  super().__init__();self.gate_proj=nn.Linear(3,5,bias=False);self.up_proj=nn.Linear(3,5,bias=False);self.down_proj=nn.Linear(5,3,bias=False)
 def forward(self,x):return self.down_proj(torch.nn.functional.silu(self.gate_proj(x))*self.up_proj(x))
class Toy(nn.Module):
 def __init__(self):
  super().__init__();self.model=nn.Module();self.model.layers=nn.ModuleList([nn.Module(),nn.Module()])
  for l in self.model.layers:l.mlp=MLP()
 def forward(self,x):
  for l in self.model.layers:x=x+l.mlp(x)
  return x
class MaskTests(unittest.TestCase):
 def setUp(self):torch.manual_seed(42);self.model=Toy();self.x=torch.randn(2,4,3)
 def test_identity(self):
  expected=self.model(self.x);c=PersistentMask(self.model,{0:[],1:[]});torch.testing.assert_close(c.forward(self.x),expected,rtol=0,atol=0)
 def test_training_and_reload(self):
  c=PersistentMask(self.model,{0:[1,4],1:[2]});seen={}
  for layer,target,_ in c.targets:
   target.register_forward_pre_hook(lambda m,args,layer=layer:seen.update({layer:args[0].detach().clone()}))
  opt=torch.optim.SGD(self.model.parameters(),lr=.1)
  original=self.model.model.layers[0].mlp.up_proj.weight.detach().clone()
  for _ in range(3):
   opt.zero_grad();y=c.forward(self.x);y.square().mean().backward()
   for layer,indices in c.coordinates.items():
    self.assertTrue(torch.all(seen[layer][...,indices]==0))
    self.assertTrue(torch.all(self.model.model.layers[layer].mlp.up_proj.weight.grad[indices]==0))
   opt.step()
  self.assertFalse(torch.equal(original,self.model.model.layers[0].mlp.up_proj.weight))
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'model.pt';c.save(p);r=PersistentMask.restore(Toy(),p)
   torch.testing.assert_close(c.forward(self.x),r.forward(self.x),rtol=0,atol=0)
   self.assertEqual(r.coordinates,c.coordinates)
   with self.assertRaises(FileExistsError):c.save(p)
 def test_unmasked_coordinates_preserved(self):
  mlp=self.model.model.layers[0].mlp
  before=torch.nn.functional.silu(mlp.gate_proj(self.x))*mlp.up_proj(self.x)
  c=PersistentMask(self.model,{0:[1]});seen=[]
  mlp.down_proj.register_forward_pre_hook(lambda m,args:seen.append(args[0].detach().clone()))
  c.forward(self.x);torch.testing.assert_close(seen[0][...,[0,2,3,4]],before[...,[0,2,3,4]],rtol=0,atol=0)
 def test_tamper_and_missing_hook(self):
  c=PersistentMask(self.model,{0:[1]});target=c.targets[0][1];target._wdfg_mask[1]=1
  with self.assertRaises(Invalid):c.forward(self.x)
  target._wdfg_mask[1]=0;c.handles[0].remove()
  with self.assertRaises(Invalid):c.forward(self.x)
 def test_contract_invalid(self):
  for spec in [{3:[0]},{0:[5]},{0:[1,1]},{}]:
   with self.assertRaises(Invalid):PersistentMask(Toy(),spec)
 def test_bypassed_layer(self):
  c=PersistentMask(self.model,{0:[1]});self.model.forward=lambda x:x
  with self.assertRaises(Invalid):c.forward(self.x)
 def test_corrupt_checkpoint(self):
  c=PersistentMask(self.model,{0:[1]})
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x';c.save(p);data=torch.load(p,weights_only=True);data['state_dict']['model.layers.0.mlp.down_proj._wdfg_mask'][1]=1;torch.save(data,p)
   with self.assertRaises(Invalid):PersistentMask.restore(Toy(),p)

class T0Tests(unittest.TestCase):
 def args(self):return dict(records=[dict(candidate_id='layer0-neuron2',predictive_score=.2,marginal_effect=.01,conditional_effect=.02,contribution=.3,matched_rank=1)],lineage=dict(model_revision='fixture-only',mask_sha256='a'*64,dataset_sha256='b'*64,protocol_sha256='c'*64,run_id='fixture-t0'))
 def test_immutable_and_tamper(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'t0.json';sha=write_t0(p,**self.args());original=p.read_bytes()
   with self.assertRaises(FileExistsError):write_t0(p,**self.args())
   self.assertEqual(p.read_bytes(),original);self.assertEqual(verify_t0(p,sha)['run_kind'],'fixture')
   e=json.loads(p.read_text());e['payload']['records'][0]['conditional_effect']=.5;p.write_text(json.dumps(e))
   with self.assertRaises(Invalid):verify_t0(p,sha)
 def test_development_separate(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'original';a=write_t0(p,**self.args());q=Path(t)/'development';b=write_t0(q,**self.args(),development_parent=a)
   self.assertNotEqual(a,b);self.assertEqual(verify_t0(p,a)['development_parent'],None);self.assertEqual(verify_t0(q,b)['scientific_status'],'NOT_EVALUATED')
 def test_missing_lineage(self):
  args=self.args();del args['lineage']['mask_sha256']
  with self.assertRaises(Invalid):write_t0('/tmp/should-not-be-created-wdfg',**args)
