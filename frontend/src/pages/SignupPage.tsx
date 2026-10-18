import { BenchmarkForm } from '../components/BenchmarkForm'

export function SignupPage() {
  return (
    <BenchmarkForm
      page="/signup"
      title="Create your profile"
      description="A local-only signup demonstration. No account will be created."
      submitLabel="Sign up"
      fields={[
        { name: 'name', label: 'Full name', required: true },
        {
          name: 'email',
          label: 'Email address',
          type: 'email',
          placeholder: 'visitor@example.invalid',
          required: true,
        },
        { name: 'canaryPhrase', label: 'Canary phrase', required: true },
        { name: 'phone', label: 'Phone (optional)', type: 'tel' },
        { name: 'address', label: 'Address (optional)' },
      ]}
    />
  )
}
