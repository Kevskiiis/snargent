# Snargent

Snargent is a full-stack application with a Vite/React frontend and a
Fastify/TypeScript backend. The recommended development environment is the
VS Code Dev Container included in this repository.

## Setup

### 1. Install the required tools

Install these tools on your computer:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or another
	Docker Engine compatible with VS Code Dev Containers
- The VS Code
	[Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

You do not need to install Node.js, npm, TypeScript, or Make on your host
machine. They are provided by the development container.

Make sure Docker Desktop is running before opening the project in the
container. On Linux, make sure your user can run Docker without `sudo`.

### 2. Get the repository

Clone the repository, then open the repository folder in VS Code:

```bash
git clone <repository-url>
cd snargent
code .
```

The folder you open must be the project root. It is the folder containing
`Makefile`, `frontend`, `backend`, and `.devcontainer`.

### 3. Reopen the project in the container

When VS Code detects `.devcontainer/devcontainer.json`, it may show a
notification asking whether to reopen the folder in a container. Select
**Reopen in Container**.

If the notification does not appear:

1. Open the Command Palette with `Ctrl+Shift+P` on Windows/Linux or
	 `Cmd+Shift+P` on macOS.
2. Run **Dev Containers: Reopen in Container**.
3. Wait for Docker to build the image and for VS Code to reconnect.

The first build can take a few minutes. The container uses Node 22 and
installs the system tools needed by the project, including `make` and `git`.

After the container is created, its `postCreateCommand` runs `make install`.
That installs dependencies for both the frontend and backend. Wait for this
command to finish before starting the application.

You can confirm that the terminal is inside the container by running:

```bash
node --version
npm --version
make --version
```

### 4. Configure the backend environment

The backend has sensible development defaults. To create an explicit local
configuration, run this from the project root inside the container:

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

Open a terminal in VS Code, make sure the terminal is in `/workspace`, and
run:

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

VS Code forwards ports `5173` and `3000` from the container to your computer.
If VS Code shows a forwarded-port notification, use the provided link or the
local URLs above.

## Common commands

Run these commands from the project root inside the container:

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

### The container will not build

Confirm Docker Desktop is running, then run **Dev Containers: Rebuild
Container** from the VS Code Command Palette. Rebuilding is safe; dependency
installation runs again after the container is recreated.

### Dependencies are missing

Run this from the project root inside the container:

```bash
make install
```

If the installation is corrupted, run `make clean`, then `make install`.

### Port 3000 or 5173 is already in use

Stop the process using the port, or change the backend `PORT` in
`backend/.env`. The frontend port can be changed in the Vite configuration.
Keep the forwarded-port configuration and the service configuration aligned.

### `make` or `node` is not found

Check that the VS Code window says **Dev Container** in the lower-left corner.
If it does not, run **Dev Containers: Reopen in Container** and open a new
terminal after VS Code reconnects.

### The frontend loads but API requests fail

Confirm that `make dev` started both processes and that
<http://localhost:3000/health> responds. Check the backend terminal for the
startup error before changing frontend code.
