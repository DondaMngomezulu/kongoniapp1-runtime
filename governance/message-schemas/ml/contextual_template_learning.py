"""Offline contextual template recommender, engineering candidate only.

This module does not connect to CRM, authenticate registry records, issue business
messages, alter templates or authorise release. Only pre-validated, independently
attested metadata may be supplied by the future trusted adapter.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from math import exp
import json
import re

FEATURE_VERSION = "ctx-template-features-0.1"
CONTEXT_KEYS = frozenset({
    "value_stream", "intent", "document_class", "channel", "issuer_entity",
    "stage", "audience", "contract_type", "locale", "available_fields",
})
REQUIRED_CONTEXT = frozenset({
    "value_stream", "intent", "document_class", "channel", "issuer_entity", "stage"
})
FIELD_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
HASH_RE = re.compile(r"^[a-f0-9]{64}$")


class InvalidContext(ValueError):
    """Structured context is not safe for feature extraction."""


def validate_context(context: dict) -> dict:
    """Allow only governed, non-personal categorical features; reject raw text."""
    if not isinstance(context, dict):
        raise InvalidContext("CONTEXT_NOT_OBJECT")
    if set(context) - CONTEXT_KEYS:
        raise InvalidContext("UNAPPROVED_CONTEXT_FEATURE")
    if REQUIRED_CONTEXT - set(context):
        raise InvalidContext("MISSING_CONTEXT_FEATURE")
    for key, value in context.items():
        if key == "available_fields":
            if not isinstance(value, list) or not all(
                isinstance(v, str) and FIELD_NAME_RE.fullmatch(v) for v in value
            ):
                raise InvalidContext("INVALID_BINDING_NAMES")
        elif not isinstance(value, str) or not 0 < len(value) <= 80 or not re.fullmatch(r"[A-Za-z0-9_+.-]+", value):
            raise InvalidContext("INVALID_CONTEXT_CATEGORY")
    return dict(context)


def _semantically_matches(context: dict, template: dict) -> bool:
    """Class/issuer/channel/stage compatibility cannot be learned away."""
    if template.get("issuer_entity") != context["issuer_entity"]:
        return False
    if template.get("value_stream") != context["value_stream"]:
        return False
    if context["intent"] not in template.get("intents", []):
        return False
    if context["document_class"] not in template.get("document_classes", []):
        return False
    if context["channel"] not in template.get("channels", []):
        return False
    allowed_contracts = template.get("allowed_contract_types", [])
    if allowed_contracts and context.get("contract_type") not in allowed_contracts:
        return False
    allowed_locales = template.get("allowed_locales", [])
    if allowed_locales and context.get("locale") not in allowed_locales:
        return False
    allowed_stages = template.get("allowed_stages", [])
    if allowed_stages and context["stage"] not in allowed_stages:
        return False
    return True


def _published(template: dict) -> bool:
    """Metadata-only filter; external release service must verify its receipt."""
    return (template.get("status") == "CONTROLLED"
            and bool(template.get("approval_ref"))
            and isinstance(template.get("sha256"), str)
            and bool(HASH_RE.fullmatch(template["sha256"]))
            and bool(template.get("version")))


def _ranking_features(context: dict, template: dict) -> dict[str, float]:
    tid = template["template_id"]
    features = {"bias": 1.0, "tpl=" + tid: 1.0}
    for key in ("intent", "stage", "audience", "contract_type", "locale", "value_stream", "channel"):
        val = context.get(key)
        if val:
            features[f"tpl={tid}|{key}={val}"] = 1.0
    if context.get("audience") in template.get("preferred_audiences", []):
        features["preferred_audience_match"] = 1.0
    return features


def _dot(weights: dict, features: dict) -> float:
    return sum(weights.get(key, 0.0) * val for key, val in features.items())


class PairwiseTemplateRanker:
    """Small supervised pairwise linear ranker, with human-curated labels only.

    Not a probability estimator and not a release policy decision point. A larger
    model can replace this with the same contract after separate evaluation.
    """
    def __init__(self):
        self.weights: dict[str, float] = {}
        self.reviewed_events = 0
        self.pairs = 0

    def fit(self, events: list[dict], templates: list[dict], *,
            trusted_training_receipt_verified=False, epochs=24, learning_rate=0.20) -> dict:
        if trusted_training_receipt_verified is not True:
            return self.model_card()
        candidates_by_id = {t["template_id"]: t for t in templates}
        pairs = []
        allowed_event_keys = {"event_id", "context", "reviewer_verified", "learning_allowed",
                              "feedback", "chosen_template_id", "presented_template_ids"}
        for event in sorted(events, key=lambda e: e.get("event_id", "")):
            if set(event) - allowed_event_keys:
                continue  # No raw messages, contact details or unrestricted features.
            if not (event.get("reviewer_verified") is True
                    and event.get("learning_allowed") is True
                    and event.get("feedback") == "ACCEPTED"):
                continue
            context = validate_context(event["context"])
            chosen = event.get("chosen_template_id")
            shown = event.get("presented_template_ids", [])
            if chosen not in shown or chosen not in candidates_by_id:
                continue
            # Training requires original exposed options, not unshown negatives.
            positive = candidates_by_id[chosen]
            if not (_semantically_matches(context, positive) and _published(positive)):
                continue
            negatives = [candidates_by_id[i] for i in sorted(set(shown))
                         if i != chosen and i in candidates_by_id
                         and _semantically_matches(context, candidates_by_id[i])
                         and _published(candidates_by_id[i])]
            if not negatives:
                continue
            a = _ranking_features(context, positive)
            for neg in negatives:
                b = _ranking_features(context, neg)
                difference = {key: a.get(key, 0) - b.get(key, 0) for key in (a.keys() | b.keys())}
                difference = {key: value for key, value in difference.items() if value}
                pairs.append(difference)
            self.reviewed_events += 1
        self.pairs = len(pairs)
        for _ in range(epochs):
            for diff in pairs:
                margin = max(-40.0, min(40.0, _dot(self.weights, diff)))
                gradient = 1.0 / (1.0 + exp(margin))
                for name, value in sorted(diff.items()):
                    self.weights[name] = self.weights.get(name, 0.0) + learning_rate * gradient * value
        return self.model_card()

    def score(self, context: dict, template: dict) -> float:
        return _dot(self.weights, _ranking_features(context, template))

    def model_card(self) -> dict:
        weights_json = json.dumps({k: round(v, 8) for k, v in sorted(self.weights.items())}, sort_keys=True)
        return {"feature_schema": FEATURE_VERSION,
                "model_sha256": sha256(weights_json.encode("ascii")).hexdigest(),
                "reviewed_events": self.reviewed_events, "training_pairs": self.pairs,
                "lifecycle": "ENGINEERING_CANDIDATE", "may_authorise_send": False}


def recommend(context: dict, templates: list[dict], *, ranker=None,
              registry_receipt_verified=False, min_reviewed_events=3, min_margin=0.10) -> dict:
    """Return review-only suggestions, never an issued/published recommendation."""
    context = validate_context(context)
    if registry_receipt_verified is not True:
        return {"decision": "ABSTAIN", "reason": "UNVERIFIED_REGISTRY", "suggestions": []}
    matching_all = [t for t in templates if _semantically_matches(context, t)]
    controlled = [t for t in matching_all if _published(t)]
    if not controlled:
        return {"decision": "ABSTAIN", "reason": "GOVERNANCE_HOLD" if matching_all else "NO_SEMANTIC_MATCH",
                "suggestions": []}
    available = set(context.get("available_fields", []))
    complete = [t for t in controlled if set(t.get("required_fields", [])) <= available]
    if not complete:
        missing = sorted(set().union(*(set(t.get("required_fields", [])) - available for t in controlled)))
        return {"decision": "ABSTAIN", "reason": "MISSING_SOURCE_BINDINGS",
                "missing_fields": missing, "suggestions": []}
    ranker = ranker or PairwiseTemplateRanker()
    ordered = sorted(complete, key=lambda t: (-ranker.score(context, t), t["template_id"]))
    results = [{"template_id": t["template_id"], "version": t["version"],
                "score": round(ranker.score(context, t), 5)} for t in ordered]
    if len(ordered) > 1 and ranker.reviewed_events < min_reviewed_events:
        return {"decision": "ABSTAIN", "reason": "INSUFFICIENT_REVIEWED_LABELS", "suggestions": results}
    if len(ordered) > 1 and ranker.score(context, ordered[0]) - ranker.score(context, ordered[1]) < min_margin:
        return {"decision": "ABSTAIN", "reason": "AMBIGUOUS_RANKING", "suggestions": results}
    return {"decision": "REVIEW_ONLY", "reason": "POLICY_COMPATIBLE_SUGGESTION",
            "suggestions": results, "selected": results[0]["template_id"]}


def discover_proposals(signals: list[dict], templates: list[dict], *,
                       registry_receipt_verified=False, distinct_case_threshold=3) -> list[dict]:
    """Identify repetitive governed coverage/edit gaps; never create actual templates."""
    if registry_receipt_verified is not True:
        return []
    grouped: dict[tuple, set[str]] = defaultdict(set)
    descriptions: dict[tuple, dict] = {}
    for signal in signals:
        allowed_signal_keys = {"reviewer_verified", "learning_allowed", "reason", "context",
                               "pseudonymous_case_token", "template_id", "edit_reason_code"}
        if set(signal) - allowed_signal_keys:
            continue
        if signal.get("reviewer_verified") is not True or signal.get("learning_allowed") is not True:
            continue
        if signal.get("reason") not in {"NO_APPROVED_SEMANTIC_TEMPLATE", "REPEATED_REVIEW_EDIT"}:
            continue
        context = validate_context(signal["context"])
        case = signal.get("pseudonymous_case_token")
        if not isinstance(case, str) or not HASH_RE.fullmatch(case):
            continue
        template_id = signal.get("template_id") if signal["reason"] == "REPEATED_REVIEW_EDIT" else None
        reason_code = signal.get("edit_reason_code") if template_id else None
        if template_id and reason_code not in {"REQUIRED_FIELD", "CLARITY", "CHANNEL_LAYOUT", "TONE"}:
            continue
        key = (signal["reason"], context["value_stream"], context["intent"], context["document_class"],
               context["channel"], context["issuer_entity"], template_id, reason_code)
        grouped[key].add(case)
        descriptions[key] = {"value_stream": context["value_stream"], "intent": context["intent"],
                             "document_class": context["document_class"], "channel": context["channel"],
                             "issuer_entity": context["issuer_entity"]}
    proposals = []
    for key in sorted(grouped, key=str):
        cases = grouped[key]
        if len(cases) < distinct_case_threshold:
            continue
        reason, _, _, _, _, _, template_id, edit_code = key
        descriptor = descriptions[key]
        if reason == "REPEATED_REVIEW_EDIT":
            related = next((t for t in templates if t.get("template_id") == template_id), None)
            if related is None:
                continue
            proposals.append({"proposal": "REVISE_EXISTING_CANDIDATE", "template_id": template_id,
                              "edit_reason_code": edit_code, "distinct_cases": len(cases),
                              "context": descriptor, "lifecycle": "REVIEW_ONLY"})
        else:
            # Presence of *any* match, including DRAFT or HOLD, must not
            # cause duplicate template creation. Promote/remediate it first.
            probe = dict(descriptor)
            probe.update({"stage": "", "available_fields": []})
            existing = [t for t in templates if _semantically_matches(probe, t)]
            # Stage-restricted templates are checked separately below so a
            # different stage does not accidentally create duplicate masters.
            if not existing:
                existing = [t for t in templates if t.get("issuer_entity") == descriptor["issuer_entity"]
                            and t.get("value_stream") == descriptor["value_stream"]
                            and descriptor["intent"] in t.get("intents", [])
                            and descriptor["document_class"] in t.get("document_classes", [])
                            and descriptor["channel"] in t.get("channels", [])]
            proposals.append({"proposal": "REVIEW_EXISTING_CANDIDATE" if existing else "PROPOSE_NEW_CANDIDATE",
                              "similar_templates": sorted(t["template_id"] for t in existing),
                              "distinct_cases": len(cases), "context": descriptor,
                              "lifecycle": "REVIEW_ONLY", "canonical_id": None})
    return proposals