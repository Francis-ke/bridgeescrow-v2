import { useState } from 'react'
import BalanceCard from './BalanceCard'

export default function WalletBalances({ balances, busy, showStatements, onStatements }) {
  const [view, setView] = useState(null)
  const website = balances?.website_sandbox
  const hasWebsite = website?.application_count > 0
  const selected = view || (balances?.payment_mode === 'daraja_live' ? 'account' : 'sandbox')
  const sandbox = hasWebsite && selected === 'sandbox'
  const available = sandbox ? website.available : balances?.available
  const held = sandbox ? website.escrow : balances
    ? (Number(balances.escrow) + Number(balances.incoming_escrow || 0)).toFixed(2) : null
  return <div className="space-y-3">
    {hasWebsite && <>
      <div className="flex gap-2" role="group" aria-label="Balance environment">
        {[['sandbox', 'Website sandbox'], ['account', 'My wallet']].map(([value, label]) =>
          <button type="button" key={value} aria-pressed={selected === value} onClick={() => setView(value)}
            className={`rounded-lg px-3 py-2 text-xs ${selected === value ? 'bg-teal-400/15 text-teal-300' : 'bg-navy-800 text-slate-400'}`}>{label}</button>)}
      </div>
      <p className="text-xs leading-relaxed text-slate-400">{sandbox
        ? 'Simulated website payments across your applications. Held payments move to Available Balance after buyer-authorized release, less fees. These funds cannot be withdrawn.'
        : 'Your account wallet. Simulated website payments are shown separately under Website sandbox.'}</p>
    </>}
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
      <BalanceCard title="Available Balance" amount={available}
        description={sandbox ? 'Sandbox · Released website earnings after fees' : 'Available to send, spend or withdraw'}
        action={sandbox ? 'View Website Transactions' : busy ? 'Loading…' : showStatements ? 'Hide Statements' : 'View Statements'}
        to={sandbox ? '/developers/api' : undefined} onClick={onStatements} />
      <BalanceCard title="Escrow Balance" amount={held}
        description={sandbox ? 'Sandbox · Website payments held until buyer confirmation' : 'Held securely until delivery is confirmed'}
        action={sandbox ? 'View Website Transactions' : 'View Escrows'} to={sandbox ? '/developers/api' : '/escrows'} />
    </div>
  </div>
}
