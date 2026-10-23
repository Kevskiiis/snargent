# Verification evidence

The current smoke matrix is generated at `harness/results/smoke/`.
It runs five baseline and five attack trials against the real Vite/React and
Fastify services, covering all five fixtures. The five attack trials are a
scripted positive control and are not model outcomes.

Any future live evidence should be generated under a fresh `harness/results/`
directory after the pinned Ollama preflight passes. Do not copy incomplete
runtime attempts into this curated evidence directory.

All data is synthetic. Runtime failures, preflight failures, and incomplete
trials are reported as errors rather than security results.
