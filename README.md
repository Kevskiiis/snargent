# Snargent

Snargent is a full-stack application with a Vite/React frontend and a
Fastify/TypeScript backend. You can develop locally with Node.js; Docker and
the VS Code Dev Containers extension are not required.

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

Run the following from the project root to install frontend and backend
dependencies:

```bash
make install
```

### 3. Configure the backend environment

The backend has sensible development defaults. To create an explicit local
configuration, run this from the project root:

```bash
cp backend/.env.example backend/.env
```

The local `.env` file is ignored by Git. The default values are:

```dotenv
HOST=0.0.0.0
PORT=3000
```

Do not commit secrets or personal environment files. Add only safe example
values to `backend/.env.example`.

## Run the application

From the project root, start both development servers:

```bash
make dev
```

This starts both services:

- Frontend: Vite on port `5173`
- Backend: Fastify on port `3000`

Open the frontend at <http://localhost:5173>. The backend health check is
available at <http://localhost:3000/health> and should return:

```json
{"status":"ok"}
```

The frontend and backend run in watch mode, so source changes are picked up
automatically. Keep the terminal running while developing. Press `Ctrl+C` to
stop both services.

## Common commands

Run these commands from the project root:

```bash
make install  # Install frontend and backend dependencies
make dev      # Start frontend and backend development servers
make build    # Build frontend and backend
make check    # Type-check the backend
make lint     # Lint the frontend
make clean    # Remove generated build output
make preview  # Serve the built frontend locally
```

For a production-style local check, build first and then preview the frontend:

```bash
make build
make preview
```

The backend production entrypoint is generated at `backend/dist/server.js` by
`make build`. It can be started separately with:

```bash
npm --prefix backend start
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
├── .devcontainer/    # Dev Container image and VS Code settings
└── Makefile          # Project-wide development commands
```

## Troubleshooting

### Dependencies are missing

Run this from the project root:

```bash
make install
```

If the installation is corrupted, run `make clean`, then `make install`.

### `make`, `node`, or `npm` is not found

Install the missing tool and make sure it is on your `PATH`. On Windows, use
WSL2 or another environment that provides GNU Make, and install Node.js inside
that environment.

### Port 3000 or 5173 is already in use

Stop the process using the port, or change the backend `PORT` in
`backend/.env`. The frontend port can be changed in the Vite configuration.
Use the updated port when opening the frontend or backend in your browser.

### The frontend loads but API requests fail

Confirm that `make dev` started both processes and that
<http://localhost:3000/health> responds. Check the backend terminal for the
startup error before changing frontend code.
