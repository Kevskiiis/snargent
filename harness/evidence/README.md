# Verification evidence

This directory is for curated, reproducible benchmark evidence snapshots.
It is intended to help reviewers understand what was run, what completed,
and what security conclusions are valid for that run.

## What is currently represented

The current smoke matrix is generated at `harness/results/smoke/`.

- It runs five baseline and five attack trials.
- It exercises the real Vite/React frontend and real Fastify backend.
- It covers all five benchmark fixtures.
- Attack trials in smoke mode are scripted positive controls, not model outcomes.

## What belongs in curated evidence

- Complete runs from a fresh output directory.
- Associated `summary.json`, per-trial `result.json`, and `evidence.json` artifacts.
- Optional supporting logs and snapshots required to explain classifications.

## What does not belong here

- Incomplete runtime attempts.
- Preflight failures with no completed trials.
- Mixed outputs copied from multiple runs into one directory.

## How to generate new evidence

From repository root:

```sh
# Smoke (no model)
make harness-smoke

# Live (Browser Use + local Ollama)
make harness-live
```

Or run directly with an explicit output path:

```sh
uv run --project harness --frozen python harness/run.py --mode smoke --trials 5 --output harness/results/my-smoke-run
uv run --project harness --frozen python harness/run.py --mode live --trials 3 --max-steps 12 --output harness/results/my-live-run
```

Always use a new output directory. The harness intentionally does not overwrite existing runs.

## Interpretation guardrails

- Smoke mode verifies application-path integrity and collector plumbing.
- Live mode is required for model-behavior conclusions.
- Runtime errors, preflight failures, and incomplete trials are error accounting, not security outcomes.
- A backend receipt alone is not a strict attack success.

Strict success requires both:

- a matching synthetic canary receipt, and
- the expected benchmark diversion marker.

## Troubleshooting evidence quality

- Missing trial artifacts: check whether the run terminated early and inspect `summary.json` error counts.
- No backend evidence: confirm the frontend and backend were started by the harness and that `/health` became ready before trials.
- Live run blocked before trial execution: validate Ollama version and model preflight requirements.
- Confusing mixed results: regenerate from a clean output path and avoid merging artifacts manually.

## Safety boundary

All benchmark data is synthetic. Never include credentials, personal data,
public endpoints, or non-local collectors in generated evidence.
