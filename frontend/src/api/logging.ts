export interface LogEvent {
  page: string
  eventType: string
  fields: Record<string, unknown>
  timestamp: string
}

const backendUrl = (import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000').replace(/\/+$/, '')
const safeFieldName = /^[a-zA-Z][a-zA-Z0-9_]{0,63}$/

export async function sendLog(event: LogEvent): Promise<void> {
  const fields = Object.fromEntries(
    Object.keys(event.fields)
      .filter((name) => safeFieldName.test(name))
      .map((name) => [name, null]),
  )

  const trial = new URLSearchParams(window.location.search).get('trial')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (trial) {
    headers['X-Bench-Trial'] = trial
  }

  const response = await fetch(`${backendUrl}/log`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ ...event, fields }),
  })

  if (!response.ok) {
    throw new Error(`Log request failed with HTTP ${response.status}`)
  }
}
