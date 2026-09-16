import Fastify from 'fastify'
import rootRoutes from './routes/root.js'
import { settings } from './config/settings.js'

export function buildServer() {
	const server = Fastify({ logger: true })

	server.register(rootRoutes)

	return server
}

async function start() {
	const server = buildServer()

	try {
		await server.listen({ host: settings.host, port: settings.port })
	} catch (error) {
		server.log.error(error)
		process.exitCode = 1
		await server.close()
	}
}

void start()
