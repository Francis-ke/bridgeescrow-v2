import CardChip from './CardChip'

const CARD = {
  expiry: '12/29',
}

export default function VirtualCard({ holderName = 'BridgeEscrow member', cardNumber, cardCvv }) {
  const number = cardNumber?.replace(/(.{4})/g, '$1 ').trim() || 'Card number unavailable'
  return (
    <section className="w-full" aria-label="Your virtual card">
      <div className="relative aspect-[1.586/1] w-full max-w-[450px] overflow-hidden rounded-[22px] border border-teal-200/25
        bg-gradient-to-br from-teal-400 via-cyan-600 to-navy-800 p-5 shadow-[0_18px_50px_-20px_rgba(20,184,166,0.5)] sm:p-6">
        <div className="absolute -right-16 -top-20 h-52 w-52 rounded-full bg-white/10" />
        <div className="absolute -bottom-24 -left-10 h-48 w-48 rounded-full bg-navy-900/30" />
        <div className="relative flex h-full flex-col justify-between">
          <div className="flex items-center justify-between text-sm font-bold tracking-wide text-navy-900">
            <span>BridgeEscrow</span>
          </div>
          <CardChip />
          <p className="font-mono text-base tracking-[0.1em] tabular-nums text-white sm:text-xl">{number}</p>
          <div className="grid grid-cols-[minmax(0,1fr)_auto_auto] gap-3 text-white">
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-widest text-white/60">Card holder</p>
              <p className="mt-1 truncate text-xs font-semibold uppercase">{holderName}</p>
            </div>
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-widest text-white/60">Expires</p>
              <p className="mt-1 text-xs font-semibold">{CARD.expiry}</p>
            </div>
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-widest text-white/60">CVV</p>
              <p className="mt-1 text-xs font-semibold">{cardCvv || '—'}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
