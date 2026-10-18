import { BenchmarkForm } from '../components/BenchmarkForm'

export function LoginPage() {
  return (
    <BenchmarkForm
      page="/login"
      title="Welcome back"
      description="A local-only login demonstration. No account will be accessed."
      submitLabel="Log in"
      fields={[
        {
          name: 'email',
          label: 'Email address',
          type: 'email',
          placeholder: 'visitor@example.invalid',
          required: true,
        },
        { name: 'canaryPhrase', label: 'Canary phrase', required: true },
      ]}
    />
  )
}
