
# Backend

The backend is a local Fastify service used by Snargent for health checks, value-free browser event logging, and benchmark-only evidence collection used by the harness.

It binds to `127.0.0.1:8000` by default and is intended for local research only.

## What this folder contains

- Fastify server bootstrap: `server.ts`
- Runtime settings and env parsing: `config/settings.ts`
- API routes and in-memory stores: `routes/root.ts`

## Prerequisites

- Node.js 22+
- npm

From repository root, install once:

```sh
make install
```

Or install only backend dependencies:

```sh
npm --prefix backend install
```

## Run locally

From this directory:

```sh
npm install
npm run dev
```

From repository root:

```sh
npm --prefix backend run dev
```

Health check:

```sh
curl -sS http://127.0.0.1:8000/health
```

## Scripts

- `npm run dev`: run server in watch mode with `tsx`
- `npm run check`: TypeScript type-check only
- `npm run build`: compile into `dist/`
- `npm run start`: start compiled server from `dist/server.js`

## Configuration

Environment variables are read on startup.

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Interface to bind Fastify |
| `PORT` | `8000` | HTTP port |
| `CORS_ORIGIN` | `http://localhost:5173` | Only this origin is allowed |
| `BENCH_EVIDENCE` | `0` | Enables benchmark evidence endpoints when set to `1` |
| `BENCH_CANARIES` | `{}` | JSON map of trial id to SHA-256 canary hash |

If `PORT` is not an integer in `[1, 65535]`, startup fails immediately.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Service identity and status |
| `GET` | `/health` | Readiness probe |
| `GET` | `/log` | In-memory value-free application event list |
| `POST` | `/log` | Accepts event metadata and stores only safe field names |
| `GET` | `/bench/evidence` | Returns benchmark evidence when `BENCH_EVIDENCE=1`; otherwise `404` |
| `POST` | `/bench/collect` | Accepts trial/value pair and records canary-match metadata |

`POST /log` schema requires `page`, `eventType`, `fields`, and an ISO timestamp.

## How the harness uses this service

During harness runs, process-level environment variables are injected to:

- select temporary host/port,
- allow CORS from the temporary frontend URL,
- enable benchmark evidence routes,
- provide hashed synthetic canary expectations.

Benchmark mode is for local controlled experiments only.

## Troubleshooting

- `EADDRINUSE` or startup bind errors: another process is already using the port; stop it or set a different `PORT`.
- CORS request failures from frontend: verify `CORS_ORIGIN` exactly matches the frontend origin including scheme and port.
- `GET /bench/evidence` returns `404`: this is expected unless `BENCH_EVIDENCE=1`.
- Trial canary never matches: ensure `BENCH_CANARIES` is valid JSON and keyed by the same trial ids sent by the harness.
- TypeScript import/compile issues: run `npm run check` to surface diagnostics.

## Safety boundary

- Keep the service bound to loopback interfaces for this benchmark.
- Do not expose benchmark evidence endpoints on shared or public infrastructure.
- The service stores metadata and benchmark match classifications only, not submitted canary values.
