import 'dotenv/config'

const port = Number.parseInt(process.env.PORT ?? '3000', 10)

if (!Number.isInteger(port) || port < 1 || port > 65535) {
	throw new Error('PORT must be an integer between 1 and 65535')
}

export const settings = {
	host: process.env.HOST ?? '0.0.0.0',
	port,
} as const
