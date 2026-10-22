# Snargent

Snargent is a local benchmark for studying whether an AI agent follows
instructions embedded in webpage content instead of its assigned task. It is
for the university security research assignment **Track A: AI Agent Trap and
Remediation**. This is not a functioning account system. Use synthetic test
data only; never enter real credentials or personal information, and do not
use this application against real users.

The app consists of a Vite/React frontend and a Fastify/TypeScript backend.
The backend stores only event metadata and submitted field names in memory; it
never stores field values. Docker and a database are not required.

## Setup

### 1. Install the required tools

Install these tools on your computer:

- [Node.js 22](https://nodejs.org/) (npm is included with Node.js)
- Git
- GNU Make

Visual Studio Code is optional; any editor can be used. On Windows, use WSL2
with Node.js 22, Git, and Make installed inside the WSL distribution, or use
another environment that provides Make.

Check that the tools are available:

```bash
node --version
npm --version
git --version
make --version
```

### 2. Get the repository

```bash
git clone https://github.com/Kevskiiis/snargent.git
cd snargent
```

### 3. Install dependencies

From the repository root:

```bash
make install
```

This runs `npm install` in both `frontend/` and `backend/`.

### 4. Configure environment (optional)

The defaults work without any configuration. Only create these files if you
need to change a port or the backend host:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

- `backend/.env`: `PORT` (default `8000`) and `HOST` (default `127.0.0.1`).
- `frontend/.env`: `VITE_BACKEND_URL` (default `http://localhost:8000`). If you
  change `PORT`, update this value to match.

Keep `HOST=127.0.0.1` unless you need another machine to reach the backend.
Setting `HOST=0.0.0.0` exposes the event log to your network.

The `.env` files are ignored by Git. Restart `make dev` after editing them.

### 5. Start both servers
From the repository root:

```bash
make dev
```

This starts the frontend and backend together in one terminal. Then open:

| Resource | URL |
| --- | --- |
| Article page (`/`) | <http://localhost:5173> |
| Signup page | <http://localhost:5173/signup> |
| Login page | <http://localhost:5173/login> |
| Backend health check | <http://localhost:8000/health> (returns `{"status":"ok"}`) |
| In-memory event log | <http://localhost:8000/log> |

Press `Ctrl+C` in the terminal to stop both servers. The Vite dev server
listens on all network interfaces (`--host 0.0.0.0`), so the frontend is
reachable from other devices on your network. The backend CORS policy allows
only `http://localhost:5173`.

### Running without Make

Use two terminals, one per application:

```bash
# Terminal 1: backend
cd backend
npm install
npm run dev
```

```bash
# Terminal 2: frontend
cd frontend
npm install
npm run dev
```

## Make targets

Run these from the repository root:

| Command | What it does |
| --- | --- |
| `make install` | Install frontend and backend dependencies |
| `make dev` | Start the frontend (port 5173) and backend (port 8000) together |
| `make build` | Build the backend and the frontend |
| `make check` | Type-check the backend |
| `make lint` | Lint the frontend with ESLint |
| `make preview` | Serve the production frontend build (run `make build` first) |
| `make clean` | Delete `dist/` and `.vite/` build output |

The frontend type-check is included in its build. To run it alone, use
`npm --prefix frontend run check`.

## Project layout

```text
.
├── backend/
│   ├── config/       # Environment-backed settings
│   ├── routes/       # Fastify routes (/health, /log)
│   └── server.ts     # Backend entrypoint and CORS policy
├── frontend/
│   └── src/
│       ├── api/          # sendLog shared logging function
│       ├── components/   # Shared form and page-view logger
│       └── pages/        # Article, signup, and login pages
└── Makefile          # Project-wide development commands
```

## Troubleshooting

### Dependencies are missing

Run `make install` from the repository root, or run `npm install` in the
affected `frontend/` or `backend/` directory.

### `make`, `node`, or `npm` is not found

Install the missing tool and make sure it is on your `PATH`. On Windows, run
everything inside WSL2 (Ubuntu or another distribution) with Node.js 22, Git,
and Make installed there.

### Port 8000 or 5173 is already in use

Find the process with `lsof -i :8000` (or `:5173`) and stop it. Alternatively,
change `PORT` in `backend/.env` and `VITE_BACKEND_URL` in `frontend/.env` to
match.

### The frontend loads but logging or API requests fail

The frontend is calling a different backend address from the one that is
running. The backend port comes from `PORT` in `backend/.env` (default `8000` when unset),
and the frontend uses `VITE_BACKEND_URL` in `frontend/.env` (default
`http://localhost:8000`). Make sure these match, then
restart `make dev`. Confirm the backend responds with
`curl http://localhost:<PORT>/health`.

### Changes to `.env` files have no effect

Stop `make dev` with `Ctrl+C`, then start it again. Vite reads environment
variables only at startup.

## D2 experiment

The attack-surface report, pinned Python harness, and exact reproduction commands
are in [harness/README.md](harness/README.md). The submission PDF is
[output/pdf/D2-Snargent.pdf](output/pdf/D2-Snargent.pdf).

Quick local plumbing check (no model or additional packages required):

```sh
python harness/run.py --mode smoke --trials 3 --output harness/results/smoke
```

Smoke results are simulated controls. Use the documented live command to test
the Browser Use/Ollama victim.
