import 'dotenv/config'

const port = Number.parseInt(process.env.PORT ?? '8000', 10)

if (!Number.isInteger(port) || port < 1 || port > 65535) {
	throw new Error('PORT must be an integer between 1 and 65535')
}

export const settings = {
	host: process.env.HOST ?? '127.0.0.1',
	port,
	corsOrigin: process.env.CORS_ORIGIN ?? 'http://localhost:5173',
	benchmarkEvidence: process.env.BENCH_EVIDENCE === '1',
	benchmarkCanaries: process.env.BENCH_CANARIES ?? '{}',
} as const
