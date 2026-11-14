import { useState } from 'react'
import { Link } from 'react-router-dom'
import { auth } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'
import { Alert, Button, Card, Field } from '../components/ui'

export default function Account() {
  const { user } = useAuth()
  return <AccountDetails key={user.id} user={user} />
}

function AccountDetails({ user }) {
  const { updateUser } = useAuth()
  const [name, setName] = useState(user.full_name || '')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  async function save(event) {
    event.preventDefault()
    setBusy(true); setError(''); setSaved(false)
    try {
      const result = await auth.updateProfile({ full_name: name.trim() })
      updateUser(result.user); setName(result.user.full_name); setSaved(true)
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  const details = [
    ['Account number', user.account_number], ['Email', user.email],
    ['National ID', user.national_id || 'Not provided'],
    ['Phone', user.phone_verified ? user.phone : 'No verified phone'],
    ['Account type', user.role],
  ]
  return <div className="mx-auto max-w-2xl space-y-6">
    <header><h1 className="text-2xl font-semibold">My account</h1>
      <p className="mt-2 text-sm text-slate-400">View your account details and update your name.</p></header>
    <Card><form onSubmit={save} className="space-y-4">
      <Field label="Full name" value={name} required minLength={3} maxLength={120}
        autoComplete="name" disabled={busy}
        onChange={(event) => { setName(event.target.value); setSaved(false) }} />
      <Alert>{error}</Alert>
      {saved && <p role="status" className="text-sm text-teal-300">Your details have been saved.</p>}
      <Button disabled={busy}>{busy ? 'Saving…' : 'Save details'}</Button>
    </form></Card>
    <Card><dl className="space-y-4">
      {details.map(([label, value]) => <div key={label}>
        <dt className="text-sm text-slate-400">{label}</dt>
        <dd className="mt-1 break-words">{value}</dd>
      </div>)}
    </dl><Link to="/phone" className="mt-6 inline-block text-sm text-teal-300">
      Manage verified phone number
    </Link></Card>
  </div>
}
