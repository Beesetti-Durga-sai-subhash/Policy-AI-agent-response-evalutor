from __future__ import annotations

from typing import Any

from .eligibility import eligible_chunk_ids
from .meaning import contains_required_fact, find_prohibited_claims

PASS = "PASS"
FAIL = "FAIL"
NOT_EVALUATED = "NOT_EVALUATED"


def check(
    rule: str,
    risk_area: str,
    expected: Any,
    observed: Any,
    verdict: str,
    reason: str,
) -> dict:
    return {
        "rule": rule,
        "risk_area": risk_area,
        "expected": expected,
        "observed": observed,
        "verdict": verdict,
        "reason": reason,
    }


def evaluate_recording(
    recording: dict,
    corpus: dict[str, dict],
    expected: dict,
    prohibited_claims: list[dict],
) -> list[dict]:
    return [
        response_contract(recording),
        expected_outcome(recording, expected),
        provider_error_mapping(recording),
        generation_control(recording),
        citation_eligibility(recording, corpus),
        context_eligibility(recording, corpus),
        quotation_integrity(recording, corpus),
        required_evidence(recording, expected),
        required_fact(recording, expected),
        prohibited_claim_check(recording, prohibited_claims),
    ]


def response_contract(recording: dict) -> dict:
    http_status = recording["observed"].get("http_status")
    body = recording["observed"].get("body")
    reason = "Response follows the required business or error body shape."
    valid = isinstance(body, dict)

    if valid and http_status == 200:
        status = body.get("status")
        answer = body.get("answer")
        citations = body.get("citations")
        valid = status in {"ANSWERED", "INSUFFICIENT_EVIDENCE", "CONFLICT"}
        valid = valid and isinstance(citations, list)
        if status == "ANSWERED":
            valid = (
                valid
                and isinstance(answer, str)
                and bool(answer.strip())
                and len(citations) >= 1
            )
        elif status == "INSUFFICIENT_EVIDENCE":
            valid = valid and answer is None and citations == []
        elif status == "CONFLICT":
            valid = valid and answer is None and len(citations) >= 2
    elif valid and http_status in {400, 401, 502, 503}:
        error = body.get("error")
        valid = (
            set(body) == {"error"}
            and isinstance(error, dict)
            and isinstance(error.get("code"), str)
            and bool(error["code"].strip())
            and isinstance(error.get("message"), str)
            and bool(error["message"].strip())
        )
    else:
        valid = False

    if not valid:
        reason = "Response does not follow the contract for its HTTP status."
    return check(
        "response_contract",
        "response_contract",
        "Valid business body for 200, or safe error body for 400/401/502/503",
        {"http_status": http_status, "body": body},
        PASS if valid else FAIL,
        reason,
    )


def expected_outcome(recording: dict, expected: dict) -> dict:
    observed_http = recording["observed"].get("http_status")
    body = recording["observed"].get("body", {})
    expected_value = {"http_status": expected["http_status"]}
    observed_value = {"http_status": observed_http}

    if expected["http_status"] == 200:
        expected_value["status"] = expected["business_status"]
        observed_value["status"] = body.get("status")
        valid = expected_value == observed_value
    else:
        expected_value["error_code"] = expected["error_code"]
        observed_code = body.get("error", {}).get("code")
        observed_value["error_code"] = observed_code
        valid = (
            expected["http_status"] == observed_http
            and isinstance(observed_code, str)
            and bool(observed_code.strip())
        )

    return check(
        "expected_outcome",
        "response_contract",
        expected_value,
        observed_value,
        PASS if valid else FAIL,
        expected["rationale"] if valid else f"Observed outcome conflicts with the requirement: {expected['rationale']}",
    )


def provider_error_mapping(recording: dict) -> dict:
    event = recording.get("trace", {}).get("provider_event")
    http_status = recording["observed"].get("http_status")
    mapping = {"timeout": 503, "unavailable": 503, "malformed": 502}
    if event not in mapping:
        return check(
            "provider_error_mapping",
            "error_handling",
            "503 for timeout/unavailable; 502 for malformed output",
            {"provider_event": event, "http_status": http_status},
            NOT_EVALUATED,
            "This recording has no provider failure to map.",
        )

    expected_status = mapping[event]
    body = recording["observed"].get("body", {})
    valid = http_status == expected_status and "error" in body
    return check(
        "provider_error_mapping",
        "error_handling",
        {"http_status": expected_status, "body_type": "error"},
        {
            "provider_event": event,
            "http_status": http_status,
            "body_type": "error" if "error" in body else "business",
        },
        PASS if valid else FAIL,
        "Provider failures must be service errors, not business outcomes."
        if not valid
        else "Provider failure is mapped to the required service error.",
    )


def generation_control(recording: dict) -> dict:
    trace = recording.get("trace")
    if not isinstance(trace, dict):
        return check(
            "generation_control",
            "error_handling",
            "Trace evidence showing at most one attempt and no generation for invalid requests",
            None,
            NOT_EVALUATED,
            "No trace was supplied, so generation controls cannot be established.",
        )

    attempts = trace.get("generation_attempts")
    event = trace.get("provider_event")
    context = trace.get("model_context_ids")
    observed = {
        "generation_attempts": attempts,
        "provider_event": event,
        "model_context_ids": context,
    }
    valid = isinstance(attempts, int) and 0 <= attempts <= 1
    reason = "Trace shows no more than one generation attempt."

    if recording["observed"].get("http_status") in {400, 401}:
        valid = valid and attempts == 0 and event == "not_called" and context == []
        reason = (
            "Invalid request did not invoke generation."
            if valid
            else "Invalid requests must have zero attempts, not_called, and empty context."
        )
    elif event == "not_called":
        valid = valid and attempts == 0
    else:
        valid = valid and attempts == 1

    return check(
        "generation_control",
        "error_handling",
        "At most one attempt; invalid requests are not sent to generation",
        observed,
        PASS if valid else FAIL,
        reason,
    )


def citation_eligibility(recording: dict, corpus: dict[str, dict]) -> dict:
    citations = recording["observed"].get("body", {}).get("citations")
    eligible = eligible_chunk_ids(recording, corpus)
    if citations is None or eligible is None:
        return check(
            "citation_eligibility",
            "access_and_eligibility",
            "Every cited chunk is approved and matches caller tenant, role, and date",
            None,
            NOT_EVALUATED,
            "Citation or valid caller/date evidence is unavailable.",
        )

    cited = [item.get("chunk_id") for item in citations]
    invalid = [chunk_id for chunk_id in cited if chunk_id not in eligible]
    return check(
        "citation_eligibility",
        "access_and_eligibility",
        {"eligible_chunk_ids": sorted(eligible)},
        {"cited_chunk_ids": cited, "ineligible_citations": invalid},
        PASS if not invalid else FAIL,
        "All citations satisfy metadata eligibility."
        if not invalid
        else "At least one citation is not eligible for this caller and date.",
    )


def context_eligibility(recording: dict, corpus: dict[str, dict]) -> dict:
    context_ids = recording.get("trace", {}).get("model_context_ids")
    eligible = eligible_chunk_ids(recording, corpus)
    if context_ids is None or eligible is None:
        return check(
            "generation_context_eligibility",
            "access_and_eligibility",
            "Every context chunk is approved and matches caller tenant, role, and date",
            context_ids,
            NOT_EVALUATED,
            "Full context trace or valid caller/date evidence is unavailable.",
        )

    invalid = [chunk_id for chunk_id in context_ids if chunk_id not in eligible]
    return check(
        "generation_context_eligibility",
        "access_and_eligibility",
        {"eligible_chunk_ids": sorted(eligible)},
        {"model_context_ids": context_ids, "ineligible_context_ids": invalid},
        PASS if not invalid else FAIL,
        "All generation context passages satisfy metadata eligibility."
        if not invalid
        else "Ineligible policy text was sent to generation.",
    )


def quotation_integrity(recording: dict, corpus: dict[str, dict]) -> dict:
    citations = recording["observed"].get("body", {}).get("citations")
    if not citations:
        return check(
            "quotation_integrity",
            "evidence_integrity",
            "Every citation quote is non-empty verbatim text from its cited passage",
            citations,
            NOT_EVALUATED,
            "There are no citation quotes to check.",
        )

    invalid = []
    for citation in citations:
        passage = corpus.get(citation.get("chunk_id"))
        quote = citation.get("quote")
        if (
            passage is None
            or not isinstance(quote, str)
            or not quote
            or quote not in passage["text"]
        ):
            invalid.append(citation)

    return check(
        "quotation_integrity",
        "evidence_integrity",
        "Non-empty verbatim quotation from the cited corpus passage",
        {"citations": citations, "invalid_citations": invalid},
        PASS if not invalid else FAIL,
        "Every quote is genuine corpus text."
        if not invalid
        else "At least one quote is absent from the cited passage.",
    )


def required_evidence(recording: dict, expected: dict) -> dict:
    citations = recording["observed"].get("body", {}).get("citations")
    if citations is None:
        return check(
            "required_evidence",
            "evidence_integrity",
            expected["required_citation_ids"],
            None,
            NOT_EVALUATED,
            "The observed body has no citation field to evaluate.",
        )

    cited_ids = [citation.get("chunk_id") for citation in citations]
    required = expected["required_citation_ids"]
    valid = set(required).issubset(cited_ids)
    return check(
        "required_evidence",
        "evidence_integrity",
        {"required_citation_ids": required},
        {"cited_chunk_ids": cited_ids},
        PASS if valid else FAIL,
        "Required supporting or conflict evidence is present."
        if valid
        else "The response omits evidence required by the expected outcome.",
    )


def required_fact(recording: dict, expected: dict) -> dict:
    fact = expected.get("required_fact")
    answer = recording["observed"].get("body", {}).get("answer")
    if fact is None:
        return check(
            "required_fact",
            "answer_meaning_and_safety",
            None,
            answer,
            NOT_EVALUATED,
            "This expected outcome has no factual answer to check.",
        )
    if not isinstance(answer, str):
        return check(
            "required_fact",
            "answer_meaning_and_safety",
            fact,
            answer,
            FAIL,
            "A supported factual answer was required but no answer string was returned.",
        )

    valid, observed = contains_required_fact(answer, fact)
    return check(
        "required_fact",
        "answer_meaning_and_safety",
        fact,
        observed,
        PASS if valid else FAIL,
        "Answer contains the required amount and currency."
        if valid
        else "Answer does not contain the independently expected amount and currency.",
    )


def prohibited_claim_check(recording: dict, claim_rules: list[dict]) -> dict:
    answer = recording["observed"].get("body", {}).get("answer")
    if not isinstance(answer, str):
        return check(
            "prohibited_claims",
            "answer_meaning_and_safety",
            "No approval, payment guarantee, or remaining-balance claim",
            answer,
            NOT_EVALUATED,
            "There is no answer text to inspect.",
        )

    found = find_prohibited_claims(answer, claim_rules)
    return check(
        "prohibited_claims",
        "answer_meaning_and_safety",
        [],
        found,
        PASS if not found else FAIL,
        "No prohibited financial claims were found."
        if not found
        else "Answer makes a claim the assistant has no authority or data to support.",
    )
