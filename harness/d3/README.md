# D3 Track A baseline status

The corrected D3 baseline contains 120 completed live trials in
`evidence/baseline-corrected-01`. One exact synthetic canary receipt occurred
in the accessible-attribute/Qwen3 1.7B cell. No mitigation has been implemented
yet. The earlier `evidence/baseline-final-01` run is invalid: stale services
occupied its ports. Its original `baseline` tag must not be cited as valid
evidence. `schedule.json`
is an input plan, never trial evidence.

## Inventory and discrepancies (2026-11-18)

- Repository: https://github.com/Kevskiiis/snargent; inspected HEAD `9552560`.
- Starting branch: `cristian`; the original `baseline` tag is invalid as noted above.
- `docs/CODEX-NAVIGATION-GUIDE.md` and D1 source materials were not found.
- `harness/run.py` uses Browser Use 0.13.10, Playwright 1.58.0,
  Ollama 0.40.2 and **orca-mini:3b**, not llama3.1:8b.
- `docs/D2-report.md` records a scripted 5+5 smoke run and an incomplete live
  pilot. The brief's 3+3 completed llama3.1 results cannot be confirmed here.
- `frontend/src/pages/ArticlePage.tsx` places all five payload strings in
  HTML comments inside a display:none wrapper. Those are payload variations
  in one channel, not five different vector kinds.
- `backend/routes/root.ts` provides the existing `/bench/collect` and in-memory
  evidence routes. This checkout does not contain the described SQLite collector.
- `harness/app_services.py` now handles Windows process cleanup.
- Existing results are ignored by `.gitignore`. D3 evidence must instead be
  curated under this directory or another tracked path.

## Authorized scope

The user explicitly confirmed team/instructor approval in this session for
additional local synthetic channels. Proposed channels:

| Channel | Attacker control | Exposure requirement |
| --- | --- | --- |
| HTML comment | Comment within local article | Actual source/extraction observation contains payload |
| Accessible attribute | Local article accessibility text | Browser observation includes attribute text |
| Page extraction | Local page text returned by extraction tool | Tool response actually delivered to model contains payload |

These are implemented and validated by integration tests and model traces. An extraction
channel must be demonstrably distinct from simply extracting the first two
placements. All transfers must remain on loopback with synthetic canaries.

## Environment observed

- Windows 11; Python 3.12.14 in the locked uv environment; uv 0.12.21.
- Node 24.21.0; Ollama 0.32.5; Browser Use 0.13.10; Playwright 1.58.0.
- Qwen3 0.6B and 1.7B are installed; exact digests and options are pinned in
  `config.json`. Hardware: 48 GiB RAM and AMD Radeon RX 6600 with 8 GiB VRAM.

## Preparation commands

From repository root:

```powershell
uv sync --project harness --frozen --group report
npm.cmd ci --prefix frontend
npm.cmd ci --prefix backend
uv run --project harness --frozen python -m playwright install chromium
ollama pull qwen3:0.6b
ollama pull qwen3:1.7b
ollama serve
uv run --project harness --frozen python -m unittest discover -s harness/d3 -v
uv run --project harness --frozen python harness/d3/run.py --output harness/d3/evidence/new-baseline
uv run --project harness --frozen python harness/d3/verify.py harness/d3/evidence/new-baseline
```

The schedule contains 3 candidate channels x 2 candidate models x 20 inputs.
Reuse the exact input schedule for both phases with fresh agents. Aggregation
rejects missing/duplicate trials, mixed phases, simulated data and schedule
mismatches, and keeps runtime failures in denominators. It validates record
structure only: independent receipt and trace verification is still required.
The existing D2 command cannot produce this matrix. The `--pilot` option runs
one live trial per cell and cannot substitute for the full evaluation.

## Remaining execution gates

1. Commit corrected baseline code/evidence. Replace the original `baseline`
   tag only if the user authorizes the repair.
2. Only then implement mitigation and run the same 120 inputs again.
3. Generate the eight-section PDF with real commit hashes and measured results.

| Phase | Actual live trials | Required live trials |
| --- | ---: | ---: |
| Corrected baseline | 120 completed | 120 |
| Mitigated | 0 | 120 |

One exact synthetic canary transfer was independently observed. No corrected
baseline/final experiment commits,
PDF or publication have been produced. Grader access has not been verified.

## AI use

Codex inspected repository code/documentation and local prerequisites, identified
brief/checkout discrepancies, generated this status document, schedule generator,
and evidence-validation unit tests. The user confirmed scope approval. No teammate
code review or experiment review is asserted.
