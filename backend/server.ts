import Fastify from 'fastify'
import { pathToFileURL } from 'node:url'
import cors from '@fastify/cors'
import rootRoutes from './routes/root.js'
import { settings } from './config/settings.js'

export function buildServer() {
	const server = Fastify({ logger: true })

	server.register(cors, {
		origin: (origin, callback) => {
			callback(null, origin === 'http://localhost:5173' ? origin : false)
		},
		methods: ['GET', 'POST'],
	})
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

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
	void start()
}
