import { useState, type FormEvent, type ReactNode } from 'react'
import { Alert, Box, Button, Stack, TextField, Typography } from '@mui/material'
import { sendLog } from '../api/logging'

interface BenchmarkField {
  name: string
  label: string
  type?: string
  required?: boolean
  placeholder?: string
}

interface BenchmarkFormProps {
  page: string
  title: string
  description: string
  submitLabel: string
  fields: BenchmarkField[]
  footer?: ReactNode
}

export function BenchmarkForm({
  page,
  title,
  description,
  submitLabel,
  fields,
  footer,
}: BenchmarkFormProps) {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const fieldNames = [...new FormData(form).keys()]

    setMessage('')
    setError('')

    try {
      await sendLog({
        page,
        eventType: 'form_submit',
        fields: Object.fromEntries(fieldNames.map((name) => [name, null])),
        timestamp: new Date().toISOString(),
      })
      form.reset()
      setMessage('Submission received. No account was created.')
    } catch (submissionError) {
      console.error('Unable to log benchmark form submission:', submissionError)
      setError('The local benchmark logger could not be reached. No account was created.')
    }
  }

  return (
    <Box className="benchmark-card">
      <Stack component="form" spacing={2.5} onSubmit={handleSubmit}>
        <Box>
          <Typography
            variant="h2"
            component="h1"
            sx={{ fontSize: '1.6rem', fontWeight: 700, lineHeight: 1.2, mb: 0.75 }}
          >
            {title}
          </Typography>
          <Typography color="text.secondary" sx={{ fontSize: '0.95rem' }}>
            {description}
          </Typography>
        </Box>
        {fields.map((field) => (
          <TextField
            key={field.name}
            name={field.name}
            label={field.label}
            type={field.type ?? 'text'}
            required={field.required ?? false}
            placeholder={field.placeholder}
            autoComplete="off"
            fullWidth
          />
        ))}
        <Button type="submit" variant="contained" size="large" disableElevation sx={{ py: 1.25 }}>
          {submitLabel}
        </Button>
        {message && (
          <Alert severity="success" variant="outlined">
            {message}
          </Alert>
        )}
        {error && (
          <Alert severity="error" variant="outlined">
            {error}
          </Alert>
        )}
        {footer}
      </Stack>
    </Box>
  )
}
