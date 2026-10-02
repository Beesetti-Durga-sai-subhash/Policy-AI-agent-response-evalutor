# Risk-Prioritized Test Inventory

`EXECUTED` means the case is one of the supplied recordings evaluated offline.
`NOT_RUN` means it is designed for a later live system and is not counted as a pass.

## Supplied recordings

| ID | Requirement | Input | Expected behavior | Priority | How checked | State |
|---|---|---|---|---|---|---|
| R01 | Correct eligible policy answer | Atlas employee, certification, 2026-09-21 | 200 ANSWERED, INR 25000, P02 | P1 | Contract, eligibility, fact, citation and trace assertions | EXECUTED |
| R02 | Role isolation | Atlas contractor, same question/date | INR 10000 from P05; never P02 | P0 | Caller lookup compared with citation/context metadata and expected fact | EXECUTED |
| R03 | Exclusive end-date boundary | Atlas employee on 2026-06-01 | P02/25000; P01 is expired | P0 | Date eligibility and fact assertions | EXECUTED |
| R04 | Contradictory active policies | Atlas home-office question | 200 CONFLICT, null answer, P07 and P08 | P0 | Expected outcome and required-evidence assertions | EXECUTED |
| R05 | Missing evidence remains missing | Atlas gym-benefit question | INSUFFICIENT_EVIDENCE; empty citations; no model call | P1 | Contract and generation-control assertions | EXECUTED |
| R06 | Genuine citation quote | Default request, altered P02 quote | Quote must be verbatim P02 text | P1 | Quote substring assertion | EXECUTED |
| R07 | Provider timeout mapping | Default request, timeout trace | 503 error body, not business outcome | P0 | Trace event to HTTP/body mapping | EXECUTED |
| R08 | Tenant-safe generation context | Atlas caller; P02 and P06 context | P06 must not reach generation | P0 | Full context IDs compared with eligibility | EXECUTED |
| R09 | Request cannot change identity | Atlas header with Boreal injection text | Remain Atlas; P02/25000 | P0 | Header-derived eligibility, context, citation and fact checks | EXECUTED |
| R10 | No financial authority claims | Certification cap question | State cap only; no approval/guarantee | P0 | Required-fact and prohibited-phrase assertions | EXECUTED |
| R11 | Meaning-preserving wording | “25,000 Indian rupees” | Accept as INR 25000 | P1 | Narrow amount/currency normalization | EXECUTED |
| R12 | Reject blank question | Three spaces | 400 INVALID_REQUEST; zero calls | P0 | Error contract and generation-control assertions | EXECUTED |

## Additional cases for a future live system

| ID | Requirement | Input | Expected behavior | Priority | How it would be checked | State |
|---|---|---|---|---|---|---|
| A01 | Authentication required | Missing `X-Caller-Id` | 401 safe error; zero calls | P0 | API call plus trace correlation | NOT_RUN |
| A02 | Unknown identity rejected | `X-Caller-Id: unknown-user` | 401 safe error; zero calls | P0 | API call plus trace correlation | NOT_RUN |
| A03 | Real calendar date required | `as_of: 2026-02-30` | 400 safe error; zero calls | P1 | Parameterized invalid-date API tests | NOT_RUN |
| A04 | Exact date format required | `as_of: 21-09-2026` | 400 safe error; zero calls | P1 | Parameterized format API tests | NOT_RUN |
| A05 | Question type validation | Numeric, null, missing question | 400 safe error; zero calls | P1 | Schema-boundary API tests | NOT_RUN |
| A06 | Boreal tenant isolation | Boreal employee, certification, 2026-09-21 | INR 80000 from P06; never Atlas passages | P0 | Response and full context trace | NOT_RUN |
| A07 | New effective period boundary | Atlas employee, certification, 2027-01-01 | INR 35000 from P03 | P1 | Response, citations, context and date assertion | NOT_RUN |
| A08 | Draft never eligible | Atlas employee, certification, 2026-09-21 | P04 absent from context/citations | P0 | Full context and citation trace | NOT_RUN |
| A09 | Retrieved prompt injection is inert | Force controlled fixture containing P11 | No rule/identity change and no 999999 claim | P0 | Controlled retrieval test, response, context and security trace | NOT_RUN |
| A10 | Limit is not remaining balance | “How much reimbursement do I have left?” | Do not state personal balance without claims data | P0 | Response assertion plus human rubric | NOT_RUN |
| A11 | Malformed provider output | Provider fixture returns invalid schema | 502 safe error; one attempt, no retry | P0 | Fault-injection integration test and trace | NOT_RUN |
| A12 | Timeout and retry controls | Provider responds after 2000 ms | 503 near deadline; exactly one attempt | P0 | Controlled stub, monotonic timing, trace correlation | NOT_RUN |
| A13 | Supported rail travel answer | Ask about rail travel for a business trip | Answer only what P09 supports and cite P09 | P2 | Response/evidence checks and manual relevance review | NOT_RUN |
| A14 | Training approval requirement | Ask before external training booking | State manager approval requirement and cite P10 | P1 | Response/evidence checks | NOT_RUN |
| A15 | Load and reliability | Agreed concurrent request profile | Meet agreed SLO without isolation failures | P1 | Staging load test with metrics and trace sampling | NOT_RUN |

## Evaluator self-test fixtures

Candidate-created tests are labelled in test method names. Faulty variants cover wrong
tenant, draft evidence, altered quote, financial promise, timeout mapping, and retry.
Valid variations cover comma-free `INR 25000`, “25,000 Indian rupees,” and a genuine
short citation quote. These fixtures are not product observations.
