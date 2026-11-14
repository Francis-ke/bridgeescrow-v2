import { useState } from 'react'
export default function CopyValue({ label, value }) {
  const [message, setMessage] = useState('')
  async function copy() {
    try { await navigator.clipboard.writeText(value); setMessage('Copied') }
    catch { setMessage('Select the value and copy it manually.') }
  }
  return <div>
    <label className="block text-xs text-slate-400">{label}
      <div className="mt-2 flex gap-2">
        <input readOnly value={value} onFocus={(event) => event.target.select()}
          className="min-w-0 flex-1 rounded-lg border border-white/10 bg-navy-900 px-3 py-2 font-mono text-xs text-teal-200" />
        <button type="button" onClick={copy} aria-label={`Copy ${label}`}
          className="rounded-lg border border-teal-400/20 px-3 py-2 text-xs text-teal-300 hover:bg-teal-400/10">Copy</button>
      </div>
    </label>
    {message && <p role="status" className="mt-1 text-xs text-teal-300">{message}</p>}
  </div>
}
