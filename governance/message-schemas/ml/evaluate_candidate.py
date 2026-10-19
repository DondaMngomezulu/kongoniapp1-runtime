"""Offline evaluation of a candidate template ranker; no production connectors.

Test cases must be disjoint from training by pseudonymous case token and by the
trusted, separately checked evaluation time boundary. Case-token presence is
not evidence that a protected HMAC was actually used.
"""

from collections import defaultdict
from dataclasses import dataclass

from contextual_template_learning import PairwiseTemplateRanker, recommend, validate_context


@dataclass(frozen=True)
class EvalMetrics:
    total_cases: int
    recommendation_coverage: float
    conditional_top1: float | None
    all_case_top1: float
    recall_at_3: float
    refused_cases: int
    wrong_template_class: int
    by_slice: dict


def evaluate_offline(train_events, test_cases, templates, *,
                     training_receipt_verified=False,
                     registry_receipt_verified=False,
                     disjoint_split_attested=False):
    """Measure performance without publishing, sending, or changing templates.

    A trusted input assembler must attest partition validity. This helper
    checks observed token overlap but cannot establish source approval.
    """
    if not (training_receipt_verified and registry_receipt_verified and disjoint_split_attested):
        raise ValueError('EVALUATION_AUTHORITY_OR_SPLIT_UNVERIFIED')
    if not test_cases or not train_events:
        raise ValueError('EMPTY_EVALUATION_PARTITION')
    train_tokens = {e['case_token'] for e in train_events}
    test_tokens = {e['case_token'] for e in test_cases}
    if any(not isinstance(t, str) or len(t) != 64 for t in train_tokens | test_tokens):
        raise ValueError('INVALID_PSEUDONYMOUS_CASE_TOKEN')
    if train_tokens & test_tokens:
        raise ValueError('TRAIN_TEST_CASE_LEAKAGE')

    ranker = PairwiseTemplateRanker()
    training = [{k: v for k, v in e.items() if k != 'case_token'} for e in train_events]
    card = ranker.fit(training, templates, trusted_training_receipt_verified=True)
    if card['training_pairs'] == 0:
        raise ValueError('INSUFFICIENT_TRAINING_PAIRS')

    selected = correct = top3 = wrong_class = 0
    slices = defaultdict(lambda: {'cases': 0, 'selected': 0, 'correct': 0})
    for case in test_cases:
        context = validate_context(case['context'])
        truth = case['correct_template_id']
        if not any(t['template_id'] == truth for t in templates):
            raise ValueError('UNKNOWN_TEST_GOLD_TEMPLATE')
        result = recommend(context, templates, ranker=ranker, registry_receipt_verified=True)
        key = context['value_stream'] + '|' + context['channel']
        slices[key]['cases'] += 1
        if truth in [s['template_id'] for s in result.get('suggestions', [])[:3]]:
            top3 += 1
        if result['decision'] == 'REVIEW_ONLY':
            selected += 1
            slices[key]['selected'] += 1
            if result['selected'] == truth:
                correct += 1
                slices[key]['correct'] += 1
            proposed = next(t for t in templates if t['template_id'] == result['selected'])
            if (context['intent'] not in proposed['intents']
                    or context['document_class'] not in proposed['document_classes']
                    or context['channel'] not in proposed['channels']):
                wrong_class += 1
    total = len(test_cases)
    return EvalMetrics(
        total_cases=total,
        recommendation_coverage=selected / total,
        conditional_top1=(correct / selected) if selected else None,
        all_case_top1=correct / total,
        recall_at_3=top3 / total,
        refused_cases=total - selected,
        wrong_template_class=wrong_class,
        by_slice=dict(slices),
    )
