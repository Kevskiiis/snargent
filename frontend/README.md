# Frontend

The frontend is a Vite + React + TypeScript application used by the Snargent benchmark. It serves the article page under test and sends value-free telemetry to the backend.

## What this folder contains

- Application shell and routing: `src/App.tsx`, `src/main.tsx`
- Pages for benchmark and auth flows: `src/pages/`
- Event logging helpers: `src/api/logging.ts`
- UI components used by trials: `src/components/`

## Prerequisites

- Node.js 22+
- npm

From repository root, install once:

```sh
make install
```

Or install only frontend dependencies:

```sh
npm --prefix frontend install
```

## Configuration

The frontend reads environment values at process startup.

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_BACKEND_URL` | `http://localhost:8000` | Base URL used for `/log` requests |

Trailing slashes are removed before requests are built.

## Run locally

From this directory:

```sh
npm install
npm run dev -- --host 127.0.0.1
```

From repository root:

```sh
npm --prefix frontend run dev -- --host 127.0.0.1
```

The dev server default URL is `http://localhost:5173`.

## Scripts

- `npm run dev`: start Vite dev server
- `npm run check`: TypeScript type-check
- `npm run lint`: ESLint checks
- `npm run build`: TypeScript check + production Vite build
- `npm run preview`: serve the production build locally

## Benchmark behavior

- Benchmark fixtures are rendered only for validated `?bench=` query values.
- Trial id is read from `?trial=` and forwarded in `X-Bench-Trial` for backend correlation.
- Logging sanitizes field payloads and sends only allowed field names, never user-entered field values.

This behavior supports local synthetic benchmark trials and is not intended for public deployment.

## Troubleshooting

- Frontend cannot reach backend: verify `VITE_BACKEND_URL` and confirm backend `/health` is reachable.
- CORS errors in browser console: backend `CORS_ORIGIN` must exactly match this frontend origin.
- Logs not appearing in backend `/log`: check network requests for non-2xx responses and verify `X-Bench-Trial` is set only when `trial` query parameter is present.
- Dev server unavailable on expected host: make sure `--host` was passed and no other Vite process is using the same port.
- Harness trials look stale: stop manually started frontend/backend processes and let the harness own service startup.

## Safety boundary

- Keep the application local for benchmark runs.
- Do not use real credentials or personal data in benchmark scenarios.
- Benchmark content is synthetic and intended only for controlled experiments.
