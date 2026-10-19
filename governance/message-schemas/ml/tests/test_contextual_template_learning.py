"""Synthetic-only tests; no client data, CRM connection or live publication."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'contextual_template_learning.py'
spec = importlib.util.spec_from_file_location('contextual_template_learning', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
H = 'a'*64


def ctx(audience='FINANCE', intent='FINANCE_LEASE_OFFER', document_class='FINANCE_LEASE_OFFER',
        channel='CH-EMAIL', issuer='SPH', stage='PROPOSAL', contract='FINANCE_LEASE',
        available=None):
    return {'value_stream':'VS02','intent':intent,'document_class':document_class,
            'channel':channel,'issuer_entity':issuer,'stage':stage,'audience':audience,
            'contract_type':contract,'locale':'en-ZA',
            'available_fields': ['Quotes.Account_Name','Quotes.Subject'] if available is None else available}


def template(tid='FINANCE', audience='FINANCE', status='CONTROLLED'):
    return {'template_id':tid,'version':'1.0','sha256':H,'approval_ref':'APPROVAL_123',
            'status':status,'issuer_entity':'SPH','value_stream':'VS02',
            'intents':['FINANCE_LEASE_OFFER'], 'document_classes':['FINANCE_LEASE_OFFER'],
            'channels':['CH-EMAIL'], 'allowed_stages':['PROPOSAL'],
            'allowed_contract_types':['FINANCE_LEASE'], 'allowed_locales':['en-ZA'],
            'preferred_audiences':[audience],
            'required_fields':['Quotes.Account_Name','Quotes.Subject']}


class ContextualTemplateTests(unittest.TestCase):
    def setUp(self):
        self.a = template('FINANCE','FINANCE')
        self.b = template('TECHNICAL','ENGINEERING')
        self.templates = [self.a,self.b]

    def test_unverified_register_abstains(self):
        result=m.recommend(ctx(), self.templates)
        self.assertEqual(result['reason'],'UNVERIFIED_REGISTRY')

    def test_hard_filter_blocks_held_template(self):
        result=m.recommend(ctx(), [template(status='HOLD')], registry_receipt_verified=True)
        self.assertEqual(result['reason'],'GOVERNANCE_HOLD')
        self.assertFalse(result['suggestions'])

    def test_wrong_business_class_cannot_be_selected(self):
        result=m.recommend(ctx(intent='CASH_SALE'),self.templates,registry_receipt_verified=True)
        self.assertEqual(result['reason'],'NO_SEMANTIC_MATCH')

    def test_wrong_issuer_cannot_be_selected(self):
        result=m.recommend(ctx(issuer='OTHER_ENTITY'),self.templates,registry_receipt_verified=True)
        self.assertEqual(result['reason'],'NO_SEMANTIC_MATCH')

    def test_wrong_channel_cannot_be_selected(self):
        result=m.recommend(ctx(channel='CH-WHATSAPP'),self.templates,registry_receipt_verified=True)
        self.assertEqual(result['reason'],'NO_SEMANTIC_MATCH')

    def test_wrong_contract_cannot_be_selected(self):
        result=m.recommend(ctx(contract='OPERATING_LEASE'),self.templates,registry_receipt_verified=True)
        self.assertEqual(result['reason'],'NO_SEMANTIC_MATCH')

    def test_missing_binding_is_not_a_new_template_gap(self):
        result=m.recommend(ctx(available=['Quotes.Account_Name']),self.templates,
                           registry_receipt_verified=True)
        self.assertEqual(result['reason'],'MISSING_SOURCE_BINDINGS')
        self.assertIn('Quotes.Subject',result['missing_fields'])

    def test_cold_start_abstains_when_two_eligible(self):
        result=m.recommend(ctx(),self.templates,registry_receipt_verified=True)
        self.assertEqual(result['reason'],'INSUFFICIENT_REVIEWED_LABELS')

    def test_human_review_training_changes_ranking_not_release(self):
        events=[]
        for i in range(8):
            for audience,selected in [('FINANCE','FINANCE'),('ENGINEERING','TECHNICAL')]:
                events.append({'event_id':f'{i}-{audience}', 'context':ctx(audience=audience),
                               'presented_template_ids':['FINANCE','TECHNICAL'],
                               'chosen_template_id':selected, 'feedback':'ACCEPTED',
                               'reviewer_verified':True,'learning_allowed':True})
        model=m.PairwiseTemplateRanker()
        card=model.fit(events,self.templates,trusted_training_receipt_verified=True)
        self.assertEqual(card['reviewed_events'],16)
        self.assertFalse(card['may_authorise_send'])
        a=m.recommend(ctx(audience='FINANCE'),self.templates,ranker=model,registry_receipt_verified=True)
        b=m.recommend(ctx(audience='ENGINEERING'),self.templates,ranker=model,registry_receipt_verified=True)
        self.assertEqual((a['decision'],a['selected']),('REVIEW_ONLY','FINANCE'))
        self.assertEqual((b['decision'],b['selected']),('REVIEW_ONLY','TECHNICAL'))

    def test_without_training_receipt_model_remains_untrained(self):
        model=m.PairwiseTemplateRanker()
        event={"event_id":"a","context":ctx(),"presented_template_ids":["FINANCE","TECHNICAL"],
               "chosen_template_id":"FINANCE","feedback":"ACCEPTED",
               "reviewer_verified":True,"learning_allowed":True}
        self.assertEqual(model.fit([event],self.templates)["training_pairs"],0)

    def test_reject_unreviewed_and_raw_content_training(self):
        good={'event_id':'x', 'context':ctx(), 'presented_template_ids':['FINANCE','TECHNICAL'],
              'chosen_template_id':'FINANCE','feedback':'ACCEPTED',
              'reviewer_verified':True,'learning_allowed':True}
        model=m.PairwiseTemplateRanker()
        card=model.fit([{**good, 'reviewer_verified':False},
                        {**good,'raw_customer_email':'private'},
                        {**good,'learning_allowed':False}],self.templates,trusted_training_receipt_verified=True)
        self.assertEqual(card['training_pairs'],0)

    def test_context_rejects_unapproved_personal_data(self):
        with self.assertRaises(m.InvalidContext):
            m.validate_context({**ctx(),'customer_email':'someone@example.test'})
        with self.assertRaises(m.InvalidContext):
            m.validate_context({**ctx(),'stage':'send a freeform message'})

    def test_existing_draft_prevents_duplicate_template(self):
        signals=[self.gap_signal(i) for i in range(3)]
        proposal=m.discover_proposals(signals,[template(status='DRAFT')],
                                      registry_receipt_verified=True)
        self.assertEqual(proposal[0]['proposal'],'REVIEW_EXISTING_CANDIDATE')
        self.assertIsNone(proposal[0]['canonical_id'])

    def test_no_existing_template_suggests_new_candidate_only(self):
        events=[self.gap_signal(i) for i in range(4)]
        proposals=m.discover_proposals(events,[],registry_receipt_verified=True)
        self.assertEqual(len(proposals),1)
        self.assertEqual(proposals[0]['proposal'],'PROPOSE_NEW_CANDIDATE')
        self.assertEqual(proposals[0]['lifecycle'],'REVIEW_ONLY')

    def test_gap_events_require_distinct_cases(self):
        event=self.gap_signal(0)
        proposal=m.discover_proposals([event,event,event],[],registry_receipt_verified=True)
        self.assertEqual(proposal,[])

    def test_repeated_review_edits_propose_revision(self):
        events=[dict(self.gap_signal(i),reason='REPEATED_REVIEW_EDIT',template_id='FINANCE',
                     edit_reason_code='REQUIRED_FIELD') for i in range(3)]
        proposals=m.discover_proposals(events,self.templates,registry_receipt_verified=True)
        self.assertEqual(proposals[0]['proposal'],'REVISE_EXISTING_CANDIDATE')
        self.assertEqual(proposals[0]['template_id'],'FINANCE')

    def test_unreviewed_gap_does_not_trigger(self):
        events=[{**self.gap_signal(i), 'reviewer_verified':False} for i in range(4)]
        self.assertEqual(m.discover_proposals(events,[],registry_receipt_verified=True),[])

    @staticmethod
    def gap_signal(i):
        return {'reviewer_verified':True,'learning_allowed':True,
                'reason':'NO_APPROVED_SEMANTIC_TEMPLATE','context':ctx(),
                'pseudonymous_case_token':format(i+1,'064x')}


if __name__=='__main__':
    unittest.main()