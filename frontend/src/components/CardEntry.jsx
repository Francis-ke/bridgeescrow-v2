import { useState } from 'react'

export default function CardEntry({ kind, onComplete, receivingAccount = false, fixedAmount }) {
  const receiving = kind === 'send' || receivingAccount
  const [number, setNumber] = useState('')
  const [expiry, setExpiry] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event) {
    event.preventDefault(); if (busy) return; setError('')
    const digits = number.replace(/\D/g, '')
    if (digits.length < 13 || digits.length > 19) { setError('Enter a card number with 13–19 digits.'); return }
    const data = new FormData(event.currentTarget)
    setBusy(true)
    try {
      await onComplete({ method: 'card', amount: data.get('amount'), destination: receiving ? data.get('cardholder')?.trim() || '' : data.get('destination') || '', last4: digits.slice(-4), ...(receiving ? { recipient_card: digits } : {}) })
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  const input = 'min-w-0 w-full bg-transparent px-3.5 py-3 text-base text-white outline-none placeholder:text-slate-400 focus:bg-teal-400/5'

  return (
    <form onSubmit={submit} className="rounded-2xl border border-white/10 bg-gradient-to-br from-navy-800 to-navy-900 p-5 text-white shadow-xl shadow-black/10 sm:p-6">
      <h2 className="mb-6 flex items-center gap-3 text-base font-semibold">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 4h18a1 1 0 0 1 1 1v3H2V5a1 1 0 0 1 1-1Zm-1 7h20v8a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-8Zm3 4v2h5v-2H5Z" /></svg>
        Card
      </h2>
      <p className="mb-5 text-xs text-slate-400">{receiving ? 'Enter the receiving account’s card details and the amount.' : 'Enter the card details and amount to continue.'}</p>
      {error && <p role="alert" className="mb-4 text-sm text-red-300">{error}</p>}
      <fieldset>
        <legend className="mb-2 text-sm font-medium text-slate-300">{receiving ? 'Receiving card information' : 'Card information'}</legend>
        <div className="overflow-hidden rounded-xl border border-white/15 shadow-sm focus-within:border-teal-400">
          <div className={`flex flex-wrap items-center ${receiving ? '' : 'border-b border-white/10'}`}>
            <input aria-label={receiving ? "Other account card number" : "Card number"} autoComplete={receiving ? "off" : "cc-number"} inputMode="numeric" placeholder={receiving ? "Other account’s card number" : "1234 1234 1234 1234"}
              value={number} onChange={(event) => setNumber(event.target.value.replace(/\D/g, '').slice(0, 19).replace(/(.{4})/g, '$1 ').trim())}
              required maxLength={23} className={`${input} flex-1 basis-48`} />
            {!receiving && <div aria-label="Card networks" className="flex shrink-0 items-center gap-1 px-3 pb-2 sm:pb-0">
              <span className="rounded border border-white/10 px-1 text-[9px] font-extrabold italic text-blue-200">VISA</span>
              <span className="flex rounded bg-slate-900 px-1 py-1" aria-label="Mastercard">
                <span className="h-3 w-3 rounded-full bg-red-500" /><span className="-ml-1 h-3 w-3 rounded-full bg-amber-400/90" />
              </span>
              <span className="rounded bg-blue-600 px-1 py-0.5 text-[8px] font-bold text-white">AMEX</span>
            </div>}
          </div>
          {!receiving && <div className="grid grid-cols-2 divide-x divide-white/10">
            <input aria-label="Expiry date" autoComplete="cc-exp" inputMode="numeric" placeholder="MM / YY"
              value={expiry} onChange={(event) => {
                const digits = event.target.value.replace(/\D/g, '').slice(0, 4)
                setExpiry(digits.length > 2 ? `${digits.slice(0, 2)} / ${digits.slice(2)}` : digits)
              }} required pattern="(0[1-9]|1[0-2]) / [0-9]{2}" maxLength={7} className={input} />
            <input aria-label="CVC security code" type="password" autoComplete="cc-csc" inputMode="numeric"
              required placeholder="CVC" maxLength={4} pattern="[0-9]{3,4}" className={input} />
          </div>}
        </div>
      </fieldset>
      <label className="mt-5 block text-sm font-medium text-slate-300">{receiving ? 'Account holder name' : 'Cardholder name'}
        <input name="cardholder" required autoComplete={receiving ? 'off' : 'cc-name'} placeholder={receiving ? 'Other account holder’s full name' : 'Full name on card'}
          className={`${input} mt-2 rounded-xl border border-white/15 shadow-sm focus:border-teal-400`} />
      </label>
      <label className="mt-5 block text-sm font-medium text-slate-300">Country or region
        <select autoComplete="country" defaultValue="KE"
          className="mt-2 w-full rounded-xl border border-white/15 bg-navy-900 px-3.5 py-3 text-base text-white shadow-sm outline-none focus:border-teal-400">
          <option value="KE">Kenya</option><option value="UG">Uganda</option>
          <option value="TZ">Tanzania</option><option value="RW">Rwanda</option>
          <option value="GB">United Kingdom</option><option value="US">United States</option>
        </select>
      </label>
      {kind === 'buy' && <label className="mt-5 block text-sm font-medium text-slate-300">
        Seller or business
        <input name="destination" required placeholder="Seller email or account number"
          className={`${input} mt-2 rounded-xl border border-white/15 shadow-sm focus:border-teal-400`} />
      </label>}
      <label className="mt-5 block text-sm font-medium text-slate-300">Amount (KES)
        <input name="amount" defaultValue={fixedAmount} readOnly={fixedAmount !== undefined} required type="number" min="0.01" step="0.01" placeholder="0.00"
          className={`${input} mt-2 rounded-xl border border-white/15 shadow-sm focus:border-teal-400`} />
      </label>
      <button type="submit" disabled={busy} className="mt-5 w-full rounded-xl bg-teal-400 py-3 text-sm font-semibold text-navy-900 hover:bg-teal-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-400">{busy ? 'Processing…' : 'Confirm transaction'}</button>
    </form>
  )
}
