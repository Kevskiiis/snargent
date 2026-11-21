# D3 application-backed security harness

The current harness is the D3 Track A experiment. It tests the real Snargent Vite/React frontend and Fastify backend with synthetic canaries, three distinct untrusted channels, two pinned local models, and matched baseline/mitigation matrices.

## Install

From the repository root:

```sh
make install
uv sync --project harness --frozen --group report
uv run --project harness --frozen python -m playwright install chromium
# Linux only when required:
uv run --project harness --frozen python -m playwright install-deps chromium
```

The D3 live run requires the exact pinned Ollama runtime and model digests from `d3/config.json`:

```sh
ollama serve
ollama pull qwen3:0.6b
ollama pull qwen3:1.7b
```

## Run

Run the D3 tests and a fresh full 120-trial matrix:

```sh
make d3-test
make d3-run
```

For an explicit output path:

```sh
uv run --project harness --frozen --group report python harness/d3/run.py \
  --output harness/d3/evidence/my-matrix
```

Verify a completed matrix and build the D3 PDF:

```sh
uv run --project harness --frozen --group report python harness/d3/verify.py \
  harness/d3/evidence/my-matrix
make report
```

Always use a new or empty output directory. The harness never overwrites an existing run.

## D3 protocol

Each full run schedules 20 trials for every pairing of these three distinct channels and two pinned models:

- `html_comment`: malicious text in article source
- `accessible_attribute`: malicious text in an accessibility attribute
- `page_extraction`: malicious annotation in a separate local extraction-service result

Each vector has 20 fresh-agent trials for `qwen3:0.6b` and `qwen3:1.7b`, for 120 live trials per phase. Both phases use the same schedule in `inputs.json`, settings in `d3/config.json`, payloads, and scoring rule.

The frontend's normal page-view logger sends a real request to the Fastify `/log` route. Benchmark evidence is enabled only for the harness process. The backend retains ordinary log metadata and field names, never submitted values. The `/bench/collect` route hashes a submitted value in memory, compares it with the expected synthetic trial canary, and stores only the match, length, trial, and classification.

The primary security outcome is an exact collector receipt for the per-trial synthetic canary. Task completion, payload exposure, submission attempts, collector receipts, and runtime failures are recorded separately.

## Output

A run contains:

```text
inputs.json                  Deterministic 120-trial schedule
trials.jsonl                 One raw row per scheduled trial
summary.json                 Aggregated evidence
environment.json             Versions, Git state, and input hashes
services.json                Temporary frontend/backend URLs and process IDs
backend.log                  Fastify output
frontend.log                 Vite output
<trial>/result.json          Trial classification and final answer
<trial>/model-messages.jsonl Exact model inputs proving exposure
<trial>/actions.json         Submission actions and policy decisions
<trial>/receipts.json        Backend collector evidence
<trial>/article.html         Real rendered page snapshot
<trial>/history.json         Browser Use action history
<trial>/conversation/        Saved model conversation
```

Aggregation rejects missing or duplicate trials, mixed phases, simulated data,
schedule mismatches, unsafe evidence paths, pinned model mismatches, incorrect
receipt classifications, and impossible exposure claims. Runtime errors remain
in the scheduled denominator.

## Application boundary

The service lifecycle is implemented in `app_services.py`. It starts:

```text
backend:  npm --prefix backend run dev
frontend: npm --prefix frontend run dev -- --host 127.0.0.1 --port <temporary-port>
```

The backend receives `CORS_ORIGIN` and benchmark settings through environment variables. Vite receives `VITE_BACKEND_URL` before startup, because Vite reads that value at process startup.

The browser is restricted to `127.0.0.1` by the Browser Use allowlist. This is an application-level restriction, not an OS network sandbox; never run the experiment with real data.

## Unit tests

```sh
make d3-test
```

The tests cover schedule and aggregation invariants, the authority-based
submission gate, all three real application channels, collector false-positive
handling, and Windows/POSIX evidence path compatibility.

## Troubleshooting

- **Missing Chromium:** run `uv run --project harness --frozen python -m playwright install chromium`.
- **Linux browser libraries missing:** run `uv run --project harness --frozen python -m playwright install-deps chromium`.
- **Service startup failure:** inspect `backend.log` and `frontend.log` in the run output.
- **CORS failure:** confirm the harness, rather than an old manually started Vite process, launched the frontend.
- **Empty backend evidence:** confirm the run reached the real frontend and that `/health` was available before the trial.
- **D3 preflight failure:** verify Ollama 0.32.5 and both exact model digests from `d3/config.json`.
- **Existing output:** choose a fresh `--output` directory.

## Legacy D2 harness

`harness/run.py`, `make harness-smoke`, and `make harness-live` retain the
historical D2 smoke/live harness. Those outputs and the D2 report remain
separate from the D3 evidence and are not used for D3 metrics.

## Safety and reporting

Only generated canaries are used. No credentials, accounts, public sites, external collectors, or real personal data are permitted. Review `summary.json`, each `result.json`, each `evidence.json`, and the saved traces together. Runtime failures are excluded from completed-trial rates and are never reported as model security results.
