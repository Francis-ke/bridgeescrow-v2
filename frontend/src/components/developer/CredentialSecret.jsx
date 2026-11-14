import CopyValue from './CopyValue'
export default function CredentialSecret({ value, onDismiss }) {
  return <div className="space-y-3 rounded-xl border border-amber-300/20 bg-amber-300/5 p-4">
    <div className="flex items-center justify-between gap-3"><h3 className="text-sm font-semibold text-amber-200">Save these credentials now</h3>
      <button type="button" onClick={onDismiss} className="text-xs text-slate-400 hover:text-white">Dismiss secret</button></div>
    <p className="text-xs leading-relaxed text-slate-400">The secret is displayed only once. Keep it on your backend server, never in browser code, mobile apps, or public repositories.</p>
    <CopyValue label="Sandbox public key" value={value.credential.public_key} />
    <CopyValue label="Sandbox secret key" value={value.secret_key} />
  </div>
}
