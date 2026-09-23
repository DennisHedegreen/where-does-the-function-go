"""M3 fixture-only conditional backup evidence audit. No statistical estimator."""
from decimal import Decimal
import re
from .m1 import fingerprint, finite
from .validation import Invalid

def sha(v):
    if not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v):raise Invalid('SHA-256 required')
    return v

def dec(v):
    finite(v);return Decimal(str(v))

def audit_backup(e):
    if e['run_kind']!='fixture' or e['data_kind']!='synthetic':raise Invalid('M3 only accepts synthetic fixture evidence')
    # Explicit receipt digests bind declarations to the same t0 and design.
    t0=e['t0'];sha(e['expected_t0_sha256'])
    if fingerprint(t0)!=e['expected_t0_sha256']:raise Invalid('t0 fingerprint mismatch')
    if t0['run_kind']!='fixture':raise Invalid('Unexpected t0 kind')
    for key in ('mask_sha256','dataset_sha256','protocol_sha256'):sha(t0['lineage'][key])
    if t0.get('schema')!='wdfg.t0/1' or t0.get('scientific_status')!='NOT_EVALUATED':raise Invalid('M2 fixture t0 payload required')
    candidates=[r['candidate_id'] for r in t0['records']]
    if not candidates or any(not isinstance(x,str) or not x for x in candidates) or len(set(candidates))!=len(candidates):raise Invalid('Invalid t0 candidate IDs')
    design=e['design'];design_hash=fingerprint(design)
    if design['t0_sha256']!=e['expected_t0_sha256']:raise Invalid('Design/t0 mismatch')
    if design['effect_method']!='paired_binary_risk_difference':raise Invalid('Paired binary design required')
    for key in ('ci_method','power_method','multiplicity_policy','pool_selection_rule'):
        if not isinstance(design[key],str) or not design[key].strip():raise Invalid('Explicit statistical design required')
    loss=dec(e['r1_loss'])
    if not 0<loss<=1:raise Invalid('R1 loss must be a positive proportion')
    delta=min(Decimal('.02'),Decimal('.20')*loss)
    reasons=[]
    if design['frozen_before_adaptation'] is not True:reasons.append('design_not_frozen_before_adaptation')
    if e['gate0_pass'] is not True:reasons.append('gate0_not_passed')
    if e['mask_integrity_pass'] is not True:reasons.append('mask_integrity_not_passed')
    ref=e['coax_reference']
    if ref['status']!='PASS':reasons.append('coax_reference_not_validated')
    elif ref['design_sha256']!=design_hash or not ref['source_commit'] or not ref['tolerance_rule']:
        raise Invalid('Reference receipt missing source/tolerance or design binding')
    expected_pools=design['pools']
    if len(expected_pools)<2:raise Invalid('At least two predeclared pools required')
    previous=set();pool_ids=set()
    for pool in expected_pools:
        ids=pool['candidate_ids']
        if not isinstance(pool['pool_id'],str) or not pool['pool_id'] or pool['pool_id'] in pool_ids:raise Invalid('Unique pool IDs required')
        pool_ids.add(pool['pool_id'])
        current=set(ids)
        if len(current)!=len(ids) or not current<=set(candidates) or not previous<current:raise Invalid('Pools must strictly expand within t0 candidates')
        previous=current
    if previous!=set(candidates):raise Invalid('Final pool does not cover declared t0 candidates')
    if len(e['pools'])!=len(expected_pools):raise Invalid('Missing expansion evidence')
    matrix=[]
    for plan,actual in zip(expected_pools,e['pools']):
        if actual['pool_id']!=plan['pool_id'] or actual['design_sha256']!=design_hash:raise Invalid('Pool identity or frozen design changed')
        rows=actual['candidates']
        if len(rows)!=len(plan['candidate_ids']) or {r['candidate_id'] for r in rows}!=set(plan['candidate_ids']):raise Invalid('Incomplete candidate evidence')
        ok=True
        for r in rows:
            counts=r['paired_counts']  # 10: phenotype present with H mask, lost after candidate co-ablation
            if set(counts)!={'00','01','10','11'} or any(type(n)is not int or n<0 for n in counts.values()):raise Invalid('Paired binary counts required')
            n=sum(counts.values())
            if n<1:raise Invalid('Empty paired sample')
            effect=Decimal(counts['10']-counts['01'])/Decimal(n)
            ci=r['ci'];power=r['power']
            if ci['method']!=design['ci_method'] or dec(ci['confidence'])!=Decimal('.90'):raise Invalid('Paired 90% CI required')
            lo=dec(ci['low']);hi=dec(ci['high'])
            if not -1<=lo<=effect<=hi<=1:raise Invalid('CI inconsistent with observed paired effect')
            if power['method']!=design['power_method'] or power['design_sha256']!=design_hash or power['n']!=n or dec(power['delta'])!=delta:raise Invalid('Power receipt is for a different design/sample/margin')
            strength=dec(power['value'])
            if not 0<=strength<=1:raise Invalid('Invalid power')
            equivalent=(-delta<lo and hi<delta);powered=strength>=Decimal('.80')
            ok=ok and equivalent and powered
            matrix.append({'pool_id':plan['pool_id'],'candidate_id':r['candidate_id'],'paired_effect':float(effect),'n':n,'equivalent':equivalent,'powered':powered})
        if not ok:reasons.append('pool_not_powered_near_null:'+plan['pool_id'])
    near_null=not reasons
    gates=e['reconstitution_gates']
    if set(gates)!={'R0','R1','R2','R3','R4','cross_seed_replication'}:raise Invalid('Complete R0–R4 and replication evidence required')
    if any(v not in ('PASS','FAIL','UNRESOLVED') for v in gates.values()):raise Invalid('Invalid reconstitution gate status')
    strong=near_null and all(v=='PASS' for v in gates.values())
    return {'run_kind':'fixture','scientific_status':'NOT_EVALUATED','execution_authorized':False,
            'fixture_backup_state':'B0-A' if near_null else 'UNRESOLVED',
            'fixture_strong_label_available':strong,'delta':float(delta),'reasons':reasons,'evidence_matrix':matrix,
            'reconstitution_gates':gates,'design_sha256':design_hash,'evidence_sha256':fingerprint(e),
            'scope':'declared candidate pools only; B0-B/C cutoffs remain open'}
