import type { FastifyPluginAsync } from 'fastify'

const rootRoutes: FastifyPluginAsync = async (server) => {
	server.get('/', async () => ({
		name: 'snargent-api',
		status: 'ok',
	}))

	server.get('/health', async () => ({
		status: 'ok',
	}))
}

export default rootRoutes
