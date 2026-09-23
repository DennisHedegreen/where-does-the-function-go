"""Provisional fixture preflight; never silently drop cohort members or authorize runs."""
import unicodedata
from .m1 import fingerprint, verify_upstream
from .validation import Invalid

POLICY = 'synthetic-unique-answer-v1'


def preflight(records, *, data_kind):
    """Inspect declared decoded tokens, not a real tokenizer or scientific freeze.

    A unique match wholly within the verified output region is provisionally
    usable. Repeated matches need review instead of upstream's first-match choice.
    Identity/leakage errors block the entire cohort. Other exclusions retain rows.
    """
    if data_kind != 'synthetic' or not isinstance(records, list) or not records:
        raise Invalid('Nonempty synthetic cohort required; empirical path is not ready')
    source = verify_upstream()
    fields = {'example_id', 'split', 'prompt', 'tokens', 'answer_tokens',
              'output_region', 'boundaries_verified'}
    seen, prompts, output = set(), {}, []
    counts = {s: {'declared': 0, 'eligible': 0, 'excluded': 0} for s in ('train', 'validation', 'test')}
    for row in records:
        if not isinstance(row, dict) or set(row) != fields:
            raise Invalid('Exact preflight fields required')
        qid, split, prompt = row['example_id'], row['split'], row['prompt']
        if not isinstance(qid, str) or not qid or qid in seen:
            raise Invalid('Duplicate or invalid example ID')
        if split not in counts or not isinstance(prompt, str) or not prompt:
            raise Invalid('Explicit split and prompt required')
        normalized = unicodedata.normalize('NFC', prompt.replace('\r\n', '\n'))
        if normalized in prompts and prompts[normalized] != split:
            raise Invalid('Prompt overlap across splits')
        seen.add(qid); prompts[normalized] = split
        tokens, answer = row['tokens'], row['answer_tokens']
        if (not isinstance(tokens, list) or not tokens or not isinstance(answer, list)
                or any(not isinstance(t, str) for t in tokens + answer)):
            raise Invalid('Decoded token lists required')
        if type(row['boundaries_verified']) is not bool:
            raise Invalid('Boundary verification must be explicit boolean')
        region = row['output_region']
        if (not isinstance(region, (list, tuple)) or len(region) != 2
                or any(type(n) is not int for n in region)):
            raise Invalid('Explicit half-open output region required')
        start, end = region
        reasons = []
        valid = 0 <= start < end <= len(tokens)
        if not valid: reasons.append('invalid_output_region')
        if not row['boundaries_verified']: reasons.append('unverified_token_boundaries')
        answer = [t.replace('▁', ' ').replace('Ġ', ' ') for t in answer]
        matches = []
        if not answer:
            reasons.append('empty_answer_tokens')
        elif valid:
            # Match upstream's search to the end, and report matches beyond output.
            matches = [[i, i + len(answer)] for i in range(start, len(tokens) - len(answer) + 1)
                       if tokens[i:i + len(answer)] == answer]
            inside = [m for m in matches if m[1] <= end]
            if not matches: reasons.append('answer_not_found')
            if any(m[1] > end for m in matches): reasons.append('answer_outside_output')
            if len(inside) > 1: reasons.append('ambiguous_answer_matches')
        eligible = not reasons
        counts[split]['declared'] += 1
        counts[split]['eligible' if eligible else 'excluded'] += 1
        output.append({'example_id': qid, 'split': split, 'eligible': eligible,
                       'reasons': reasons, 'matches': matches,
                       'selected_region': matches[0] if eligible else None,
                       'input_sha256': fingerprint(row)})
    receipt = {'policy': POLICY, 'policy_status': 'provisional_fixture_only',
               'source_commit': source['commit'], 'data_kind': data_kind,
               'declared': len(records), 'eligible': sum(r['eligible'] for r in output),
               'excluded': sum(not r['eligible'] for r in output),
               'by_split': counts, 'records': output,
               'scientific_status': 'NOT_EVALUATED', 'execution_authorized': False}
    receipt['audit_sha256'] = fingerprint(receipt)
    return receipt
