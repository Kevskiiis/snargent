# Frontend

The frontend is a Vite/React application. It reads `VITE_BACKEND_URL` at startup and sends value-free page and form events to the backend.

```sh
npm install
npm run dev -- --host 127.0.0.1
```

The default backend URL is `http://localhost:8000`. The article benchmark fixtures are selected only with validated `?bench=` query values and are intended for the local security harness, never for public deployment.

Useful commands:

```sh
npm run check
npm run lint
npm run build
```

## Vite template notes

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
