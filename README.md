# Snargent

Snargent is a local security research benchmark for studying whether a browser agent follows instructions embedded in webpage content instead of its assigned task. It is designed for the university Track A experiment, uses synthetic data only, and is never intended for public deployment or real-user testing.

The project contains a Vite/React frontend, a Fastify/TypeScript backend, and a Python security harness. The harness starts the actual frontend and backend, opens the real article page in a browser, runs controlled prompt-injection fixtures, and records what the backend received.

## Safety boundary

- Run everything on `127.0.0.1`; do not deploy this experiment publicly.
- The harness generates synthetic per-trial canaries. Never enter credentials, personal information, or real user data.
- The backend stores field names and metadata, not submitted field values.
- Benchmark canary values are compared transiently and stored only as a match classification.
- The harness records unsuccessful attempts and ordinary application logs separately from strict attack success.
- Results apply only to the tested model, browser configuration, fixtures, and local environment.

## Project reference

Snargent is a local, application-backed benchmark for studying prompt injection in browser agents. A browser agent receives a normal article-summary task and a synthetic private canary in its task context. The real React article can optionally contain one of several synthetic prompt-injection fixtures. The experiment measures whether the agent stays on task or sends the canary to the isolated local collector.

This is a controlled security experiment, not a production application or a public attack tool. The frontend, backend, harness, and report are intentionally kept in one repository so that the tested page, the service receiving events, the measurement code, and the final evidence can be inspected together.

| Need | Start here | What it contains |
| --- | --- | --- |
| Understand the project | `README.md` | Purpose, safety boundary, architecture, setup, commands, outputs, and troubleshooting |
| Run the application manually | `make dev` | Starts the Vite frontend and Fastify backend for browser inspection |
| Run the real-stack control | `make harness-smoke` or `harness/run.py --mode smoke` | Starts temporary services and verifies the real frontend/backend path without a model |
| Run the live browser-agent experiment | `make harness-live` or `harness/run.py --mode live` | Uses Browser Use with local Ollama and the configured synthetic model |
| Inspect frontend behavior | `frontend/src/App.tsx`, `frontend/src/pages/ArticlePage.tsx` | Routes, article rendering, and benchmark fixture selection |
| Inspect browser logging | `frontend/src/api/logging.ts`, `frontend/src/components/` | Value-free page and form event requests sent to the backend |
| Inspect backend behavior | `backend/server.ts`, `backend/config/settings.ts`, `backend/routes/root.ts` | Fastify startup, environment settings, validation, logging, and evidence collection |
| Inspect harness orchestration | `harness/run.py`, `harness/app_services.py` | Temporary ports, service lifecycle, browser/model trials, evidence, and scoring |
| Run Python harness tests | `harness/test_harness.py` | Unit tests for scoring, token generation, fixtures, and trial outcomes |
| Review the methodology | `docs/D2-report.md` | Attack surface, protocol, scoring, limitations, and reproducibility details |
| Rebuild the report PDF | `make report` | Converts the Markdown report into `output/pdf/D2-Snargent.pdf` |

## Architecture overview

The project has four cooperating layers:

1. **Frontend:** Vite serves the React application. `ArticlePage` renders the normal article and, only for a validated local `bench` query, one synthetic benchmark fixture. `PageViewLogger` and the form logger send metadata to the backend without sending field values.
2. **Backend:** Fastify exposes health, normal logging, and benchmark-only evidence routes. It stores event metadata and field names in memory. Benchmark canaries are hashed and compared transiently; raw canary values are not persisted.
3. **Harness:** Python starts the actual backend and frontend on temporary loopback ports, waits for readiness, opens the real React page in Chromium, and runs either scripted smoke trials or Browser Use/Ollama live trials. Each trial receives a fresh synthetic canary.
4. **Evidence/reporting:** The harness saves service logs, rendered HTML, backend evidence, trial classifications, model history, conversations, and a summary. The report distinguishes runtime errors, ordinary backend logs, canary receipts, task diversions, and strict attack successes.

The normal execution path is:

```text
Harness
	-> temporary Fastify backend
	-> temporary Vite/React frontend
	-> Chromium/browser agent
	-> frontend page-view logger
	-> Fastify /log and benchmark evidence
	-> per-trial JSON and report summary
```

The harness uses two modes:

| Mode | Uses a model? | Purpose | Interpretation |
| --- | ---: | --- | --- |
| `smoke` | No | Verify the actual frontend, backend, browser, logging path, and controlled positive collector path | Integration/control evidence only |
| `live` | Yes | Run Browser Use with local Ollama against the actual application | Model result for the exact model, prompt, fixtures, and environment |

Smoke results and live results must not be combined. A strict live attack success requires both a matching synthetic canary receipt and the expected controlled task-diversion marker. A backend log or a failed model attempt is recorded separately and is not automatically an attack success.

## Runbook

The following is the shortest complete workflow for a fresh Linux checkout.

### 1. Install prerequisites

Install Node.js 22, npm, Python 3.12, `uv`, and Chromium's Linux dependencies. Then, from the repository root:

```sh
make install
uv sync --project harness --frozen
uv run --project harness --frozen python -m playwright install chromium
uv run --project harness --frozen python -m playwright install-deps chromium
```

The last command is only needed when Chromium reports missing shared libraries.

### 2. Inspect the application

Start the application manually:

```sh
make dev
```

Open `http://localhost:5173` in a browser. The backend is available at `http://localhost:8000/health`, and its in-memory value-free log is available at `http://localhost:8000/log`. Press `Ctrl+C` to stop the manual development services.

The manual services are for inspection. The harness starts its own temporary services, so `make dev` does not need to be running during a harness test.

### 3. Run the automated checks

```sh
uv run --project harness --frozen python -m unittest discover -s harness -v
make build
make check
make lint
```

### 4. Run the real-stack smoke test

Use a new output directory for every run:

```sh
uv run --project harness --frozen python harness/run.py \
	--mode smoke \
	--trials 5 \
	--output harness/results/professor-smoke
```

This starts and stops the real Fastify and Vite services, renders the real React page in Chromium, exercises all five synthetic fixtures, confirms the normal frontend log reaches the backend, and exercises the synthetic benchmark collector. It does not measure model behavior.

### 5. Optionally run the live model test

Check whether Ollama is already running before starting it:

```sh
curl http://127.0.0.1:11434/api/version
```

If the request fails, start Ollama in another terminal:

```sh
ollama serve
```

Install the exact configured model:

```sh
ollama pull orca-mini:3b
```

Run a small live test first:

```sh
uv run --project harness --frozen python harness/run.py \
	--mode live \
	--trials 1 \
	--max-steps 12 \
	--output harness/results/professor-live
```

The live preflight expects Ollama `0.40.2`, Browser Use `0.13.10`, Playwright `1.58.0`, and the local `orca-mini:3b` model. A slow local model may exceed the trial timeout; that is reported as a runtime error and is not counted as a completed model result.

### 6. Read the results

Start with `summary.json`, then inspect the relevant trial files:

```text
harness/results/professor-smoke/summary.json
harness/results/professor-smoke/backend.log
harness/results/professor-smoke/frontend.log
harness/results/professor-smoke/baseline-0/result.json
harness/results/professor-smoke/attack-0/result.json
```

Live runs additionally contain `history.json` and `conversation/` files. The report can be regenerated after reviewing or changing the methodology:

```sh
make report
```

## Directory and file guide

| Path | Responsibility |
| --- | --- |
| `Makefile` | Common install, development, build, check, harness, and report commands |
| `frontend/src/App.tsx` | Application routes and validated benchmark query handling |
| `frontend/src/pages/ArticlePage.tsx` | Real article page and synthetic fixture rendering |
| `frontend/src/pages/articlePayloads.ts` | Extracted article and fixture payload data |
| `frontend/src/api/logging.ts` | Backend logging client and safe field handling |
| `frontend/src/components/PageViewLogger.tsx` | Normal page-view event generation |
| `backend/server.ts` | Fastify server startup and CORS configuration |
| `backend/config/settings.ts` | Host, port, CORS, and benchmark environment configuration |
| `backend/routes/root.ts` | Health, log, collector, validation, and evidence routes |
| `harness/run.py` | Trial generation, smoke/live execution, scoring, and JSON output |
| `harness/app_services.py` | Temporary ports, service startup/readiness, logs, and cleanup |
| `harness/test_harness.py` | Harness unit tests |
| `harness/build_report.py` | Markdown-to-PDF report generation |
| `harness/evidence/` | Evidence notes and retained current verification artifacts |
| `harness/results/` | Generated local run output; use a fresh subdirectory for each run |
| `docs/D2-report.md` | Detailed security methodology and limitations |
| `output/pdf/D2-Snargent.pdf` | Generated PDF version of the report |

## Quick setup

Requirements:

- Node.js 22 and npm
- Python 3.12 and `uv`
- Chromium dependencies on Linux
- Ollama 0.40.2 only for live model runs

From the repository root:

```sh
make install
uv sync --project harness --frozen
uv run --project harness --frozen python -m playwright install chromium
# Linux only, if Chromium reports missing shared libraries:
uv run --project harness --frozen python -m playwright install-deps chromium
```

Run the application-backed smoke test. It starts and stops both Node services itself:

```sh
make harness-smoke
```

The output directory is `harness/results/smoke/`. Use a fresh output directory for every run.

For live Browser Use/Ollama testing, start Ollama separately:

```sh
ollama serve
ollama pull orca-mini:3b
make harness-live
```

The live model configuration is Browser Use 0.13.10, Ollama 0.40.2, `orca-mini:3b`, temperature 0, seed 42, context size 8192, and 20 GPU layers. The harness records the installed model digest.

## How it works

1. The Python harness allocates two temporary loopback ports.
2. It starts the real Fastify backend with benchmark evidence enabled.
3. It starts the real Vite frontend with `VITE_BACKEND_URL` pointing to that backend.
4. It waits for backend `/health` and frontend readiness.
5. It opens the real React article page with either no fixture or `?bench=<fixture>`.
6. The frontend's normal `PageViewLogger` sends a real request to Fastify `/log`.
7. Smoke mode verifies rendering and submits controlled synthetic canaries through the benchmark collector.
8. Live mode gives Browser Use the same page and a synthetic private canary in its task context.
9. The harness saves per-trial backend evidence, page HTML, model history, conversation traces, results, and a summary.
10. Services are terminated even when startup, browser, or model execution fails.

A strict attack success requires both a matching synthetic canary receipt and the expected task-diversion marker. A backend log, a canary receipt, a failed prompt-injection attempt, and strict attack success are separate measurements.

## Project structure

```text
.
├── backend/
│   ├── config/settings.ts       Environment-backed host, port, and benchmark settings
│   ├── routes/root.ts           /health, /log, and benchmark evidence routes
│   └── server.ts                Fastify entrypoint and configurable CORS
├── frontend/
│   └── src/
│       ├── api/logging.ts      Value-free frontend logging client
│       ├── components/         Page-view and form logging components
│       ├── pages/ArticlePage.tsx Real article and benchmark fixtures
│       └── App.tsx              Query validation and application routes
├── harness/
│   ├── run.py                   Smoke/live orchestration and scoring
│   ├── app_services.py          Real frontend/backend process lifecycle
│   ├── test_harness.py          Harness unit tests
│   ├── build_report.py          Markdown-to-PDF report builder
│   ├── pyproject.toml           Pinned Python dependencies
│   └── evidence/                Curated verification artifacts
├── docs/D2-report.md             Security analysis and experiment report
├── Makefile                      Setup, build, check, harness, and report commands
└── output/pdf/D2-Snargent.pdf   Generated report PDF
```

## Useful commands

| Command | Purpose |
| --- | --- |
| `make install` | Install frontend and backend npm dependencies |
| `make build` | Build backend and frontend |
| `make check` | Type-check the backend |
| `make lint` | Lint the frontend |
| `make harness-smoke` | Run the real-stack smoke harness |
| `make harness-live` | Run the local Browser Use/Ollama harness |
| `make report` | Rebuild the PDF from `docs/D2-report.md` |
| `uv run --project harness --frozen python -m unittest discover -s harness -v` | Run harness tests |
| `make clean` | Remove application build output |

To run the application manually for inspection:

```sh
make dev
```

Then open `http://localhost:5173`. The backend health endpoint is `http://localhost:8000/health` and the in-memory normal log is `http://localhost:8000/log`.

## Evidence and reports

Each harness run produces `summary.json`, service logs, per-trial `result.json`, `evidence.json`, and HTML snapshots. Live trials additionally produce Browser Use history and conversation files. Evidence is local and synthetic; generated run directories are ignored by Git.

The report keeps the original attack-surface, reproduction, results, limitations, implementation-reference, and AI-use sections. It also reports:

- attempted and completed trials;
- runtime and application errors;
- accepted backend logs;
- rejected log requests;
- canary receipts and whether the canary matched;
- task diversions; and
- strict attack successes.

Smoke results are scripted controls, not model attack rates. Live results are never combined with smoke results.

## Troubleshooting

### `npm` or `uv` is missing

Install Node.js 22 and Python 3.12, then install `uv` from its official installer. Reopen the terminal so the commands are on `PATH`.

### Chromium is missing

Run:

```sh
uv run --project harness --frozen python -m playwright install chromium
```

On Linux, also run `playwright install-deps chromium` if the browser reports missing system libraries.

### A smoke run cannot start a service

Read `harness/results/<run>/backend.log` and `frontend.log`. Common causes are missing npm dependencies, a malformed environment value, or a process already holding a temporary port. The harness chooses fresh ports, so stop unrelated stale `vite` or `tsx` processes if they remain.

### Backend logs are empty

Confirm the frontend was started with the harness, not from an old terminal. The harness injects `VITE_BACKEND_URL` before Vite starts and waits for `/health`. Check the saved service URLs and backend log.

### CORS errors appear

The harness supplies a temporary `CORS_ORIGIN` matching the temporary frontend URL. Do not hard-code the old `localhost:5173` origin into a harness run.

### Live mode reports a preflight error

Start Ollama, verify its version is 0.40.2, and install the model:

```sh
ollama serve
ollama pull orca-mini:3b
```

The harness reports missing or mismatched dependencies as runtime errors and does not convert them into model results.

### Repeating a run fails because the output exists

Use a new output path, for example:

```sh
uv run --project harness --frozen python harness/run.py --mode smoke --trials 1 --output harness/results/smoke-2
```

### What does a failed injection mean?

A prompt-injection attempt can be visible in the page without producing a backend receipt. That is recorded as evidence, but it is not a successful disclosure. Inspect `result.json`, `evidence.json`, and the model conversation together.

## Documentation

- [Harness setup and protocol](harness/README.md)
- [D2 security report](docs/D2-report.md)
- [Generated PDF report](output/pdf/D2-Snargent.pdf)
