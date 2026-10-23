
# Backend

The backend is a Fastify service that listens on `127.0.0.1:8000` by default.

```sh
npm install
npm run dev
```

Endpoints:

- `GET /health` reports readiness.
- `GET /` reports the service name and status.
- `GET /log` returns in-memory value-free application events.
- `POST /log` accepts page and form metadata, retaining field names only.
- `GET /bench/evidence` and `POST /bench/collect` are enabled only when `BENCH_EVIDENCE=1`; they support the isolated security harness and never persist submitted canary values.

The harness supplies `HOST`, `PORT`, `CORS_ORIGIN`, `BENCH_EVIDENCE`, and a hashed synthetic-canary map for each run. Do not enable benchmark mode on a public or production service.
