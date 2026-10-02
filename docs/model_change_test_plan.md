# Later Model or Prompt Change Test Plan

1. Freeze this corpus, recording schema, expected results, evaluator version, model
   identifier, prompt version, and generation settings.
2. Run each high-risk case repeatedly because model output varies. Use at least 10 runs
   per case for an initial controlled comparison; increase the sample before a release
   decision if failures are rare or unstable.
3. Add meaningful wording variations without changing intent: direct questions,
   paraphrases, boundary dates, role names, injection attempts, requests for approval,
   and multi-turn-looking instructions placed in a single question.
4. Apply the same contract, eligibility, evidence, meaning, and safety criteria to the
   baseline and candidate. Do not loosen criteria merely to favor the new version.
5. Report results per rule and risk area with run counts, including failures and
   not-evaluated outcomes. Keep individual outputs and traces for diagnosis.
6. Have a reviewer manually judge a risk-based sample and every automated failure.
7. When human and automation disagree, do not force a pass. Check the policy source and
   requirement, classify whether the expected result, evaluator rule, or human judgment
   is wrong, record the decision, and add a focused regression test before rerunning.
8. Investigate flaky cases by comparing authorized context, citations, provider event,
   attempts, prompt/model version, and exact output. Do not use repeated runs to vote away
   a security or unsupported-financial-claim failure.

No live model call is made by this repository. A later execution needs a controlled test
environment, faithful per-request traces, stable fixtures, and reviewers authorized to
resolve policy ambiguity.
