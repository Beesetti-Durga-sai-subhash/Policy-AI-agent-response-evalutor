# Release Recommendation

## Decision: NO GO

The prototype should not enter a controlled internal pilot based on the supplied
evidence. The release blockers are cross-tenant policy exposure and identity override
(R08-R09), incorrect role and date eligibility (R02-R03), silent conflict resolution
(R04), provider timeout misclassification (R07), a false claim approval and payment
guarantee (R10), and a fabricated citation quotation (R06).

Release requires evidence that tenant, role, approval state, and effective dates are
enforced before generation; request or retrieved text cannot alter identity or rules;
conflicts return `CONFLICT` with both quotations; citation text is genuine; provider
failures use the required error contract; and answers cannot claim balances, approval,
or payment. The P0/P1 live cases in the inventory should pass with full post-filter
context and attempt traces.

## Validation checks

Each recording is evaluated using the following checks:

| Check | What it validates |
|---|---|
| `response_contract` | The HTTP status and response body follow the required format. |
| `expected_outcome` | The response has the expected HTTP status and business status, such as `ANSWERED`, `CONFLICT`, or `INSUFFICIENT_EVIDENCE`. |
| `provider_error_mapping` | Provider timeouts or unavailability return HTTP 503, and malformed provider output returns HTTP 502. |
| `generation_control` | Generation is attempted no more than once and is not called for invalid input. |
| `citation_eligibility` | Every cited passage is approved and matches the caller's tenant, role, and effective date. |
| `generation_context_eligibility` | Only eligible passages are provided to the model as context. |
| `quotation_integrity` | Every citation contains a non-empty, verbatim quotation from the cited corpus passage. |
| `required_evidence` | The response cites all passages required to support the answer or report a conflict. |
| `required_fact` | The answer contains the expected amount and recognized currency wording. |
| `prohibited_claims` | The answer does not make unsupported claims about balances, approval, or guaranteed payment. |

Each applicable check receives `PASS`, `FAIL`, or `NOT_EVALUATED`. A recording fails
when at least one applicable check fails. The release decision also considers the
severity of failures, so a serious access, identity, evidence, or safety failure can
block release even when the overall number of passing checks is high.

The generated report provides check-level numerators and denominators by risk area,
including `NOT_EVALUATED`:

| Risk area | PASS | FAIL | NOT_EVALUATED | Total |
|---|---:|---:|---:|---:|
| Access and eligibility | 16 | 7 | 1 | 24 |
| Answer meaning and safety | 13 | 4 | 7 | 24 |
| Error handling | 12 | 1 | 11 | 24 |
| Evidence integrity | 15 | 5 | 4 | 24 |
| Response contract | 22 | 2 | 0 | 24 |

Recording-level results are 4/12 without a failed check and 8/12 with at least one
failure. This is not a meaningful overall product pass rate: the cases are hand-picked,
risks differ, checks overlap, and the sample is not representative.

Residual risk remains after fixes because generative responses vary and this pack is
offline. A later pilot decision needs repeated live runs, prompt variations, negative
authorization tests, deterministic provider fault injection, measured 2000 ms timeout
and no-retry behavior, load evidence, monitoring, and human review of ambiguous wording.
The current recordings cannot establish live latency, capacity, present production
behavior, or internal code-level root causes.

## Validation checks
 
Each recording is evaluated using the following checks:
 
| Check | What it validates |
|---|---|
| `response_contract` | The HTTP status and response body follow the required format. |
| `expected_outcome` | The response has the expected HTTP status and business status, such as `ANSWERED`, `CONFLICT`, or `INSUFFICIENT_EVIDENCE`. |
| `provider_error_mapping` | Provider timeouts or unavailability return HTTP 503, and malformed provider output returns HTTP 502. |
| `generation_control` | Generation is attempted no more than once and is not called for invalid input. |
| `citation_eligibility` | Every cited passage is approved and matches the caller's tenant, role, and effective date. |
| `generation_context_eligibility` | Only eligible passages are provided to the model as context. |
| `quotation_integrity` | Every citation contains a non-empty, verbatim quotation from the cited corpus passage. |
| `required_evidence` | The response cites all passages required to support the answer or report a conflict. |
| `required_fact` | The answer contains the expected amount and recognized currency wording. |
| `prohibited_claims` | The answer does not make unsupported claims about balances, approval, or guaranteed payment. |
 
Each applicable check receives `PASS`, `FAIL`, or `NOT_EVALUATED`. A recording fails
when at least one applicable check fails. The release decision also considers the
severity of failures, so a serious access, identity, evidence, or safety failure can
block release even when the overall number of passing checks is high.