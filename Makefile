.PHONY: dev install build check lint clean backend-build frontend-build backend-check frontend-lint preview

FRONTEND_DIR := frontend
BACKEND_DIR := backend

# Install dependencies for both applications.
install:
	npm --prefix $(FRONTEND_DIR) install
	npm --prefix $(BACKEND_DIR) install

# Start the frontend and backend development servers together.
dev:
	@trap 'kill $$(jobs -p) 2>/dev/null || true' INT TERM EXIT; \
	(npm --prefix $(FRONTEND_DIR) run dev -- --host 0.0.0.0) & \
	(npm --prefix $(BACKEND_DIR) run dev) & \
	wait

# Build both applications.
build: backend-build frontend-build

backend-build:
	npm --prefix $(BACKEND_DIR) run build

frontend-build:
	npm --prefix $(FRONTEND_DIR) run build

# Run available static checks.
check: backend-check

backend-check:
	npm --prefix $(BACKEND_DIR) run check

lint: frontend-lint

frontend-lint:
	npm --prefix $(FRONTEND_DIR) run lint

# Remove generated build output.
clean:
	rm -rf $(BACKEND_DIR)/dist $(FRONTEND_DIR)/dist $(FRONTEND_DIR)/.vite

# Serve the production frontend after running `make build`.
preview:
	npm --prefix $(FRONTEND_DIR) run preview -- --host 0.0.0.0
