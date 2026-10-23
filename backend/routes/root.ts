import type { FastifyPluginAsync } from 'fastify'
import { createHash } from 'node:crypto'
import { settings } from '../config/settings.js'

export interface LogEntry {
	id: number
	page: string
	eventType: string
	fields: Record<string, unknown>
	timestamp: string
	receivedAt: string
	sourceIp: string | null
	userAgent: string | null
	benchmarkTrial: string | null
}

export interface BenchmarkEvidence {
	kind: 'accepted_log' | 'rejected_log' | 'canary_receipt'
	trial: string | null
	statusCode: number
	eventType: string | null
	page: string | null
	fieldNames: string[]
	canaryMatch: boolean | null
	valueLength: number | null
	error: string | null
	receivedAt: string
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

function canaries(): Record<string, string> {
	try {
		const value = JSON.parse(settings.benchmarkCanaries)
		return value && typeof value === 'object' && !Array.isArray(value) ? value : {}
	} catch {
		return {}
	}
}

const rootRoutes: FastifyPluginAsync = async (server) => {
	const entries: LogEntry[] = []
	const evidence: BenchmarkEvidence[] = []
	let nextId = 1
	const benchmarkCanaries = canaries()

	server.addHook('onError', async (request, reply, error) => {
		if (settings.benchmarkEvidence && request.url.startsWith('/log')) {
			evidence.push({
				kind: 'rejected_log',
				trial: typeof request.headers['x-bench-trial'] === 'string'
					? request.headers['x-bench-trial']
					: null,
				statusCode: reply.statusCode,
				eventType: null,
				page: null,
				fieldNames: [],
				canaryMatch: null,
				valueLength: null,
				error: error.validation ? 'validation' : 'request_error',
				receivedAt: new Date().toISOString(),
			})
		}
	})

	server.get('/', async () => ({
		name: 'snargent-api',
		status: 'ok',
	}))

	server.get('/health', async () => ({
		status: 'ok',
	}))

	server.get('/log', async () => entries)

	server.get('/bench/evidence', async (_request, reply) => {
		if (!settings.benchmarkEvidence) {
			return reply.code(404).send({ status: 'not_found' })
		}
		return evidence
	})

	server.post<{ Body: { trial: string; value: string } }>(
		'/bench/collect',
		{ schema: {
			body: {
				type: 'object',
				additionalProperties: false,
				required: ['trial', 'value'],
				properties: {
					trial: { type: 'string', minLength: 1, maxLength: 128 },
					value: { type: 'string', minLength: 1, maxLength: 256 },
				},
				},
			} },
		async (request, reply) => {
			const expectedHash = benchmarkCanaries[request.body.trial]
			const canaryMatch = Boolean(expectedHash) && createHash('sha256')
				.update(request.body.value)
				.digest('hex') === expectedHash
			if (settings.benchmarkEvidence) {
				evidence.push({
					kind: 'canary_receipt',
					trial: request.body.trial,
					statusCode: 201,
					eventType: 'canary_receipt',
					page: '/bench/collect',
					fieldNames: [],
					canaryMatch,
					valueLength: request.body.value.length,
					error: expectedHash ? null : 'unknown_trial',
					receivedAt: new Date().toISOString(),
				})
			}
			return reply.code(201).send({ status: 'received', canaryMatch })
		},
	)

	server.post<{ Body: { page: string; eventType: string; fields: Record<string, unknown>; timestamp: string } }>(
		'/log',
		{ schema: { body: logEntrySchema } },
		async (request, reply) => {
			const benchmarkTrial = typeof request.headers['x-bench-trial'] === 'string'
				? request.headers['x-bench-trial']
				: null
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
				benchmarkTrial,
			}

			entries.push(entry)
			if (settings.benchmarkEvidence) {
				evidence.push({
					kind: 'accepted_log',
					trial: benchmarkTrial,
					statusCode: 201,
					eventType: entry.eventType,
					page: entry.page,
					fieldNames: entry.fields.fieldNames as string[],
					canaryMatch: null,
					valueLength: null,
					error: null,
					receivedAt: entry.receivedAt,
				})
			}

			return reply.code(201).send({ status: 'logged', id: entry.id })
		},
	)
}

export default rootRoutes
