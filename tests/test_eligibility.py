import copy
import unittest
from wdfg.eligibility import preflight
from wdfg.validation import Invalid


class EligibilityTests(unittest.TestCase):
    def row(self, **changes):
        return dict(example_id='a', split='train', prompt='Question?',
                    tokens=['Q', '<assistant>', ' yes', ' indeed', '<eos>'],
                    answer_tokens=['Ġyes'], output_region=[2, 4],
                    boundaries_verified=True, **{}) | changes

    def audit(self, rows): return preflight(rows, data_kind='synthetic')

    def test_unique_answer_and_denominators(self):
        receipt = self.audit([self.row(), self.row(example_id='b', split='test', prompt='Other?', answer_tokens=['missing'])])
        self.assertEqual((receipt['declared'], receipt['eligible'], receipt['excluded']), (2, 1, 1))
        self.assertEqual(receipt['records'][0]['selected_region'], [2, 3])
        self.assertEqual(receipt['records'][1]['reasons'], ['answer_not_found'])
        self.assertEqual(receipt['by_split']['test'], dict(declared=1, eligible=0, excluded=1))
        self.assertFalse(receipt['execution_authorized'])

    def test_ambiguous_match_not_silently_first(self):
        row = self.row(tokens=['Q', 'header', ' yes', ' yes', '<eos>'])
        result = self.audit([row])['records'][0]
        self.assertEqual(result['matches'], [[2, 3], [3, 4]])
        self.assertEqual(result['reasons'], ['ambiguous_answer_matches'])
        self.assertIsNone(result['selected_region'])

    def test_terminal_match_and_cross_boundary(self):
        for answer in [['<eos>'], [' indeed', '<eos>']]:
            result = self.audit([self.row(answer_tokens=answer)])['records'][0]
            self.assertIn('answer_outside_output', result['reasons'])
            self.assertFalse(result['eligible'])

    def test_missing_empty_and_unverified_boundaries(self):
        for changes, reason in [({'answer_tokens': []}, 'empty_answer_tokens'),
                                ({'boundaries_verified': False}, 'unverified_token_boundaries'),
                                ({'output_region': [4, 4]}, 'invalid_output_region')]:
            result = self.audit([self.row(**changes)])['records'][0]
            self.assertIn(reason, result['reasons'])
            self.assertIsNone(result['selected_region'])

    def test_identity_and_normalized_prompt_leakage(self):
        with self.assertRaises(Invalid): self.audit([self.row(), self.row()])
        with self.assertRaises(Invalid):
            self.audit([self.row(prompt='caf\u00e9\n'), self.row(example_id='b', split='test', prompt='cafe\u0301\r\n')])

    def test_digest_binds_input_and_row_order(self):
        rows = [self.row(), self.row(example_id='b', prompt='Different')]
        digest = self.audit(rows)['audit_sha256']
        self.assertEqual(digest, self.audit(rows)['audit_sha256'])
        self.assertNotEqual(digest, self.audit(rows[::-1])['audit_sha256'])
        changed = copy.deepcopy(rows); changed[0]['tokens'][0] = 'Changed prompt token'
        self.assertNotEqual(digest, self.audit(changed)['audit_sha256'])

    def test_empirical_and_malformed_input_refused(self):
        with self.assertRaises(Invalid): preflight([self.row()], data_kind='empirical')
        for rows in [[], [self.row(boundaries_verified='yes')], [self.row(output_region=[True, 4])], [self.row(tokens=['Q', 1])]]:
            with self.assertRaises(Invalid): self.audit(rows)
