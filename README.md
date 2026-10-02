# Policy Assistant QA Evaluation Pack

This repository evaluates 12 recorded responses from a fictional employee-policy
assistant. It works fully offline. It does not build or call an AI model, API, retrieval
service, frontend, or business application.

## What is included

- The unchanged synthetic policy corpus in `data/corpus.json`
- A faithful transcription of recording defaults and overrides in `data/recordings.json`
- Independent expected results in `data/expected_results.json`
- Reusable evaluator rules in `src/evaluator`
- Candidate-created evaluator tests in `tests`
- A machine-readable result in `reports/evaluation-report.json`
- Test inventory, expected-result reasoning, defects, release decision, and future plan in `docs`

## Architecture

```text
corpus + recordings + expected results
                  |
                  v
      loader expands supplied defaults
                  |
                  v
 reusable contract, eligibility, evidence,
 meaning, safety, and error-handling checks
                  |
                  v
     JSON report + console summary + exit code
```

Expected results are separate from observations. Checks use data and rules rather than
assigning verdicts by recording ID.

## Requirements

- Python 3.11 or newer
- No runtime or test dependencies

The evaluator and tests use only the Python standard library.

## Run the evaluation

From the repository root:

```bash
python -m src.evaluator.cli evaluate
```

The command writes `reports/evaluation-report.json`.

Exit codes:

- `0`: no product recording has a failed check
- `1`: one or more product recordings have failed checks
- `2`: the evaluator could not load inputs or write its report

Exit code `1` is expected for the supplied observations. It means the evaluator ran
successfully and found product violations.

## Test the evaluator

```bash
python -m unittest discover -s tests -v
```

These tests contain candidate-created bad responses and meaning-preserving variations.
They are tests of the evaluator, not extra product observations.

## How a recording is judged

Every applicable check reports:

- recording ID
- rule and risk area
- expected value
- observed value
- `PASS`, `FAIL`, or `NOT_EVALUATED`
- a plain-English reason

Future tests that have not been executed are documented as `NOT_RUN` in the test
inventory. Missing evidence is never counted as a pass.

The narrow meaning check recognizes the required amount and either `INR` or
`Indian rupees`. It is intentionally not a general natural-language grader. Exact
full-answer matching is not used.

## Important limits

This pack can judge only the supplied recordings. It does not prove current live-system
behavior, latency, load capacity, production reliability, the actual 2000 ms deadline,
or the behavior of a representative set of model responses. Trace checks rely on the
assessment statement that traces are faithful. Suspected causes are not claimed as known
code defects because application source is unavailable.

## Time and AI assistance

Time spent must be updated by the candidate with the honest total before submission:
`TODO: record final elapsed time (maximum allowed: 6 hours)`.

AI assistance was used to interpret the supplied assessment, structure the repository,
draft the evaluator and documentation, and review test coverage. The candidate remains
responsible for verifying the data, expected results, severity decisions, generated
report, and every statement submitted. No paid model call or external dataset is used by
the evaluator.

## Submission checklist

1. Update the honest time-spent entry above.
2. Run both commands and review the report.
3. Explain at least one assertion and its limitations without reading from notes.
4. Create a public GitHub repository without the original assessment PDF.
5. Review the final commit for credentials or private material.
6. Submit the repository URL and full final commit SHA.
