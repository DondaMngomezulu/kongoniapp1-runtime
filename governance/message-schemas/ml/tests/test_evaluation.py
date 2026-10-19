"""Synthetic-only checks for offline evaluation and leakage controls."""
import importlib.util
from pathlib import Path
import sys
import unittest

base = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(base))
spec = importlib.util.spec_from_file_location('evaluation',base/'evaluate_candidate.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
from test_contextual_template_learning import ctx, template


class EvaluateCandidateTests(unittest.TestCase):
    def setUp(self):
        self.templates=[template('FINANCE','FINANCE'),template('TECHNICAL','ENGINEERING')]
        self.train=[]
        for i in range(8):
            for audience, selected, suffix in [('FINANCE','FINANCE','01'),('ENGINEERING','TECHNICAL','02')]:
                self.train.append({
                    'event_id':f'e{i}{suffix}', 'case_token':f'{10+i*2+int(suffix):064x}',
                    'context':ctx(audience), 'presented_template_ids':['FINANCE','TECHNICAL'],
                    'chosen_template_id':selected,'feedback':'ACCEPTED',
                    'reviewer_verified':True,'learning_allowed':True})
        self.test=[{'case_token':f'{100+i:064x}',
                    'context':ctx('FINANCE' if i%2==0 else 'ENGINEERING'),
                    'correct_template_id':'FINANCE' if i%2==0 else 'TECHNICAL'}
                   for i in range(6)]

    def evaluate(self,train=None,test=None,**kwargs):
        return m.evaluate_offline(
            self.train if train is None else train, self.test if test is None else test,
            self.templates, training_receipt_verified=True,
            registry_receipt_verified=True,disjoint_split_attested=True,**kwargs)

    def test_heldout_learning(self):
        result=self.evaluate()
        self.assertEqual(result.total_cases,6)
        self.assertEqual(result.wrong_template_class,0)
        self.assertEqual(result.conditional_top1,1.0)
        self.assertEqual(result.recall_at_3,1.0)

    def test_refuses_overlap(self):
        overlapping=[{**self.test[0],'case_token':self.train[0]['case_token']}]
        with self.assertRaisesRegex(ValueError,'TRAIN_TEST_CASE_LEAKAGE'):
            self.evaluate(test=overlapping)

    def test_without_authority_refuses(self):
        with self.assertRaisesRegex(ValueError,'EVALUATION_AUTHORITY_OR_SPLIT_UNVERIFIED'):
            m.evaluate_offline(self.train,self.test,self.templates)

    def test_empty_evaluation_fails(self):
        with self.assertRaisesRegex(ValueError,'EMPTY_EVALUATION_PARTITION'):
            self.evaluate(test=[])

    def test_empty_training_fails(self):
        with self.assertRaisesRegex(ValueError,'EMPTY_EVALUATION_PARTITION'):
            self.evaluate(train=[])

    def test_untrained_after_unreviewed_only(self):
        train=[{**item,'reviewer_verified':False} for item in self.train]
        with self.assertRaisesRegex(ValueError,'INSUFFICIENT_TRAINING_PAIRS'):
            self.evaluate(train=train)

if __name__ == '__main__':
    unittest.main()
