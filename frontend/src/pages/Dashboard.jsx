import { useWalletOverview } from '../hooks/useWalletOverview'
import { useAuth } from '../context/AuthContext'
import { Alert } from '../components/ui'
import VirtualCard from '../components/VirtualCard'
import WalletBalances from '../components/WalletBalances'
import QuickActions from '../components/QuickActions'

export default function Dashboard() {
  const { user } = useAuth()
  return <AccountDashboard key={user.id} user={user} />
}

function AccountDashboard({ user }) {
  const { balances, entries, showStatements, busy, error, statements } = useWalletOverview(user.id)
  return (
    <div className="space-y-6 sm:space-y-8">
      <p className="text-sm text-slate-400">{user.full_name} · Account {user.account_number}</p>
      <Alert>{error}</Alert>
      <div className="grid items-center gap-6 lg:grid-cols-[minmax(0,450px)_minmax(0,1fr)] lg:gap-8">
        <div className="mx-auto w-full max-w-[450px]">
          <VirtualCard holderName={user?.full_name} cardNumber={user?.card_number} cardCvv={user?.card_cvv} />
        </div>
        <WalletBalances balances={balances} busy={busy} showStatements={showStatements} onStatements={statements} />
      </div>
      <QuickActions />
      {showStatements && <section id="wallet-statements" className="rounded-2xl border border-white/10 bg-navy-800 p-5">
        <h2 className="mb-4 font-semibold">Wallet statements</h2>
        {entries?.length === 0 ? <p className="text-sm text-slate-400">No transactions yet.</p>
          : <ul className="divide-y divide-white/10">{entries?.map((entry) => <li key={entry.id}
            className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
            <div className="min-w-0"><p className="break-words capitalize">{entry.description || entry.entry_type}</p>
              <p className="mt-1 break-all text-xs text-slate-400">{entry.category_label} · {entry.account_bucket} · {entry.reference}</p></div>
            <p className={entry.direction === 'credit' ? 'text-teal-400' : 'text-slate-200'}>
              {entry.direction === 'credit' ? '+' : '−'} Ksh {(Number(entry.amount_cents) / 100)
                .toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </li>)}</ul>}
      </section>}
    </div>
  )
}
