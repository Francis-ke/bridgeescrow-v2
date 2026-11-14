import { Button } from '../ui'
export default function ApiKeys({ keys, secret, onRevoke, busy }) {
  return <section className="space-y-4">
    {secret && <div className="rounded-xl border border-teal-400/30 bg-teal-400/5 p-4">
      <h2 className="font-semibold text-teal-300">Save your API key</h2>
      <p className="my-2 text-xs text-slate-400">Shown once. Keep it on your website’s server, never in browser code.</p>
      <code className="block select-all break-all text-sm text-white">{secret}</code>
    </div>}
    <h2 className="font-semibold">Your API keys</h2>
    <ul className="divide-y divide-white/10">{keys.map((key) => <li key={key.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
      <div><p>{key.name}</p><code className="text-xs text-slate-500">{key.prefix}… · {key.revoked ? 'Revoked' : 'Active'}</code></div>
      {!key.revoked && <Button variant="ghost" disabled={busy} onClick={() => onRevoke(key.id)}>Revoke</Button>}
    </li>)}</ul>
  </section>
}
