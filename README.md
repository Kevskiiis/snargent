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

Clone the repository and change to its root directory:

```bash
git clone <repository-url>
cd snargent
```

Install and start the backend in one terminal:

```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

Install and start the frontend in a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open <http://localhost:5173>. The backend listens on
<http://localhost:8000>; its health check is <http://localhost:8000/health>
and the in-memory event log is available at <http://localhost:8000/log>.

The health endpoint should return:

```json
{"status":"ok"}
```

Both servers run in watch mode. Keep both terminals open while developing;
press `Ctrl+C` in each to stop the services. The browser origin is restricted
to `http://localhost:5173`.

## Common commands

Run these commands from the relevant `frontend` or `backend` directory:

```bash
npm install     # Install dependencies
npm run dev     # Start the development server
npm run check   # Type-check the application
npm run build   # Build the application
```

## Project layout

```text
.
├── backend/
│   ├── config/       # Environment-backed settings
│   ├── routes/       # Fastify routes
│   └── server.ts     # Backend entrypoint
├── frontend/
│   └── src/          # React application source
└── Makefile          # Project-wide development commands
```

## Troubleshooting

### Dependencies are missing

Run `npm install` again from the affected `frontend` or `backend` directory.

### `make`, `node`, or `npm` is not found

Install the missing tool and make sure it is on your `PATH`. On Windows, use
WSL2 or another environment that provides GNU Make, and install Node.js inside
that environment. GNU Make is not needed for the separate-terminal setup above.

### Port 8000 or 5173 is already in use

Stop the process using the port. The backend port can be changed with `PORT`
in `backend/.env.example` and the frontend API address with
`VITE_BACKEND_URL` in `frontend/.env`.

### The frontend loads but API requests fail

Confirm that both servers are running and that
<http://localhost:8000/health> responds. Check the backend terminal for the
startup error before changing frontend code.
