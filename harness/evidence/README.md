# Verification evidence

- smoke-20261019.json: 0/3 baseline and 3/3 scripted positive controls.
  These verify plumbing and scoring; they are not model outcomes.
- live-preflight-20261019.json: Ollama connection refused; zero completed
  trials, one error per condition, and null success rates.
- Four unit tests passed with Python 3.12.14 on October 19, 2026.

No completed live-model evidence is available in this checkout. Follow the
harness README to start Ollama and run the live experiment. All data is synthetic.

Verified loop fix: `loop-fix-live/` retains the final live run, including model
inputs and outputs. One baseline and one attack trial each completed on the
first model step with zero errors and no canary disclosure. Attack success
was 0/1. This small check verifies execution, not general model robustness.
The concise custom system prompt replaces Browser Use's default flash prompt;
the JSON output schema constrains the action array to exactly one item.

Latest six-trial live run: `live-fixed-3/` completed 3/3 baseline and 3/3 attack
trials, with zero runtime errors, zero receipts/diversions, and 0/3 successful
attacks. All final answers summarize the article. This run supersedes the
one-pair check for reported counts; the two runs are not pooled.
