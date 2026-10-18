import type { FastifyPluginAsync } from 'fastify'

export interface LogEntry {
	id: number
	page: string
	eventType: string
	fields: Record<string, unknown>
	timestamp: string
	receivedAt: string
	sourceIp: string | null
	userAgent: string | null
}

const logEntrySchema = {
	type: 'object',
	additionalProperties: false,
	required: ['page', 'eventType', 'fields', 'timestamp'],
	properties: {
		page: { type: 'string', minLength: 1 },
		eventType: { type: 'string', minLength: 1 },
		fields: { type: 'object', additionalProperties: true },
		timestamp: { type: 'string', format: 'date-time' },
	},
} as const

const safeFieldName = /^[a-zA-Z][a-zA-Z0-9_]{0,63}$/

const rootRoutes: FastifyPluginAsync = async (server) => {
	const entries: LogEntry[] = []
	let nextId = 1

	server.get('/', async () => ({
		name: 'snargent-api',
		status: 'ok',
	}))

	server.get('/health', async () => ({
		status: 'ok',
	}))

	server.get('/log', async () => entries)

	server.post<{ Body: { page: string; eventType: string; fields: Record<string, unknown>; timestamp: string } }>(
		'/log',
		{ schema: { body: logEntrySchema } },
		async (request, reply) => {
			const entry: LogEntry = {
				id: nextId++,
				page: request.body.page,
				eventType: request.body.eventType,
				fields: {
					fieldNames: Object.keys(request.body.fields).filter((name) => safeFieldName.test(name)),
				},
				timestamp: request.body.timestamp,
				receivedAt: new Date().toISOString(),
				sourceIp: request.ip || null,
				userAgent: request.headers['user-agent'] ?? null,
			}

			entries.push(entry)

			return reply.code(201).send({ status: 'logged', id: entry.id })
		},
	)
}

export default rootRoutes
