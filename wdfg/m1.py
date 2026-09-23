"""M1 contracts and pure fixture scoring; no empirical authorization."""
import hashlib
import json
import math
import re
import unicodedata
from decimal import Decimal
from pathlib import Path
from .validation import ROOT, Invalid, read_json

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()

def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise Invalid('Expected finite numeric value, not boolean')
    return value

def dataset_fingerprint(records, preprocessing_version):
    """Preserve prompt whitespace; normalize Unicode NFC and CRLF only."""
    if not isinstance(preprocessing_version, str) or not preprocessing_version.strip():
        raise Invalid('Explicit preprocessing version required')
    seen = set(); prompts = {}; rows = []
    for r in records:
        required = {'example_id', 'split', 'prompt', 'parameters', 'ground_truth'}
        if not isinstance(r, dict) or set(r) != required:
            raise Invalid('Dataset record fields do not match contract')
        if not isinstance(r['example_id'], str) or not r['example_id'] or r['example_id'] in seen:
            raise Invalid('Duplicate or empty example ID, including across splits')
        if r['split'] not in ('train', 'validation', 'test') or not isinstance(r['prompt'], str) or not r['prompt']:
            raise Invalid('Invalid split or prompt')
        if not isinstance(r['parameters'], dict) or r['ground_truth'] is None:
            raise Invalid('Parameters and ground truth required')
        seen.add(r['example_id'])
        prompt = unicodedata.normalize('NFC', r['prompt'].replace('\r\n', '\n'))
        if prompt in prompts and prompts[prompt] != r['split']:
            raise Invalid('Normalized prompt leaks across splits')
        prompts[prompt] = r['split']
        rows.append({**r, 'prompt': prompt})
    if not rows: raise Invalid('Empty dataset')
    return {'sha256': fingerprint({'preprocessing_version': preprocessing_version, 'records': sorted(rows, key=lambda r:r['example_id'])}),
            'examples':len(rows), 'preprocessing_version':preprocessing_version}

def verify_upstream():
    lock = read_json(ROOT / 'upstream/h-neurons.lock.json')
    for f, expected in lock['files'].items():
        if hashlib.sha256((ROOT/'upstream/h-neurons'/f).read_bytes()).hexdigest() != expected:
            raise Invalid('Pinned upstream file modified: '+f)
    return lock

def normalize_h_neurons(example_id, split, cett, weights, *, source_commit, threshold):
    """Normalize a reviewed JSON export: layer-major CETT matrix + flat coef_[0].

    Does not unpickle a model, train a classifier, or recreate CETT extraction.
    """
    lock = verify_upstream()
    if source_commit != lock['commit']: raise Invalid('Wrong upstream commit')
    if not isinstance(example_id,str) or not example_id or split not in ('train','validation','test'):
        raise Invalid('Example identity and split required')
    if type(threshold) not in (int,float) or threshold not in (0.0005,0.001,0.002):
        raise Invalid('Protocol coefficient threshold required')
    if not isinstance(cett,list) or not cett or not isinstance(cett[0],list) or not cett[0]:
        raise Invalid('CETT matrix required')
    width=len(cett[0])
    if any(not isinstance(row,list) or len(row)!=width for row in cett) or len(weights)!=len(cett)*width:
        raise Invalid('Layer-major feature shape mismatch')
    records=[]
    for layer,row in enumerate(cett):
        for neuron,score in enumerate(row):
            weight=finite(weights[layer*width+neuron]);finite(score)
            records.append(dict(example_id=example_id,split=split,layer_index=layer,neuron_index=neuron,
                cett_score=score,classifier_weight=weight,is_h_neuron=weight>threshold,
                upstream_positive=weight>0,source_commit=source_commit,coefficient_threshold=threshold))
    return {'run_kind':'fixture','scientific_status':'NOT_EVALUATED','records':records,
            'artifact_sha256':fingerprint(records)}

def number(v, low, high):
    finite(v)
    if not low <= v <= high: raise Invalid('Metric outside valid range')
    return Decimal(str(v))

def interval(raw, estimate, method):
    if not isinstance(raw,dict) or set(raw)!={'low','high','confidence','method'}:
        raise Invalid('Interval with explicit method and confidence required')
    lo=number(raw['low'],-1,1); hi=number(raw['high'],-1,1)
    if lo>estimate or estimate>hi or raw['confidence'] != .95 or raw['method']!=method:
        raise Invalid('Invalid 95% interval, pairing or method')
    return lo>0  # touching zero does not exclude it

def gate0(evidence):
    """Score explicit fixture metrics/intervals. No CI estimator is invented here."""
    fields={'run_kind','data_kind','dataset_sha256','source_commit','seed','triviaqa','nq_open','bioasq','faith_eval','ppl'}
    if not isinstance(evidence,dict) or set(evidence)!=fields: raise Invalid('Incomplete Gate 0 evidence')
    if evidence['run_kind']!='fixture' or evidence['data_kind']!='synthetic':
        raise Invalid('M1 scorer accepts synthetic fixtures only')
    if not isinstance(evidence['dataset_sha256'],str) or not re.fullmatch('[a-f0-9]{64}',evidence['dataset_sha256']):
        raise Invalid('Dataset fingerprint required')
    if evidence['source_commit']!=verify_upstream()['commit'] or type(evidence['seed']) is not int:
        raise Invalid('Pinned source and explicit seed required')
    def advantage(metric):
        if set(metric)!={'h_accuracy','random_accuracy'}:raise Invalid('Incomplete classifier metrics')
        return number(metric['h_accuracy'],0,1)-number(metric['random_accuracy'],0,1)
    trivia=evidence['triviaqa']
    if set(trivia)!={'h_accuracy','random_accuracy','paired_ci'}: raise Invalid('Missing TriviaQA evidence')
    a=advantage({k:v for k,v in trivia.items() if k!='paired_ci'})
    ci_a=interval(trivia['paired_ci'],a,'paired')
    ood=[advantage(evidence[k]) for k in ('nq_open','bioasq')]
    faith=evidence['faith_eval']
    if set(faith)!={'baseline_compliance','h_compliance','matched_compliance','selectivity_ci'}:
        raise Invalid('Missing FaithEval controls')
    baseline=number(faith['baseline_compliance'],0,1)
    h=number(faith['h_compliance'],0,1);matched=number(faith['matched_compliance'],0,1)
    loss=baseline-h;selectivity=matched-h
    ci_c=interval(faith['selectivity_ci'],selectivity,'stratified_paired_bootstrap')
    ppl=evidence['ppl']
    if set(ppl)!={'baseline','h'}: raise Invalid('Missing perplexity evidence')
    p=finite(ppl['baseline']);q=finite(ppl['h'])
    if p<=0 or q<=0: raise Invalid('Perplexity must be positive')
    damage=(Decimal(str(q))-Decimal(str(p)))/Decimal(str(p))
    passed={'G0_A':a>=Decimal('.08') and ci_a and all(x>0 for x in ood),
            'G0_B':loss>=Decimal('.05'), 'G0_C':selectivity>=Decimal('.03') and ci_c,
            'G0_D':damage<Decimal('.10')}
    # Exactly 10%: non-pass without inventing the protocol's ambiguous boundary label.
    overall='PASS' if all(passed.values()) else ('AMBIGUOUS' if damage>Decimal('.10') else 'FAIL')
    return {'validation_status':'PASS','run_kind':'fixture','scientific_status':'NOT_EVALUATED',
            'fixture_gate_outcome':overall,'gates':{k:'PASS' if v else 'FAIL' for k,v in passed.items()},
            'effects':{'triviaqa_advantage':float(a),'faith_loss':float(loss),'selectivity':float(selectivity),'ppl_relative_increase':float(damage)},
            'evidence_sha256':fingerprint(evidence),'execution_authorized':False}
