import { useState } from 'react'
import { examples } from './examples'
import WebhookGuide from './WebhookGuide'
export default function LiveApiDocumentation() {
  const [language, setLanguage] = useState('JavaScript')
  const snippets = examples(window.location.origin, 'production')
  return <section className="space-y-4 rounded-2xl border border-teal-400/20 bg-navy-800/60 p-5">
    <h2 className="text-lg font-semibold">Production M-PESA integration</h2>
    <ol className="list-inside list-decimal space-y-3 text-sm leading-relaxed text-slate-400">
      <li>Copy this production application’s secret key to BE_SECRET on your website backend. Live keys start with be_live_sk_. Your key identifies your account as the seller.</li>
      <li>Your server loads the bill from your database and creates an escrow with a stable order reference and Idempotency-Key. Live M-PESA totals must be whole KES.</li>
      <li>Create a checkout session with method mpesa, then navigate the buyer to checkout_session.url.</li>
      <li>The buyer verifies their email and uses a phone verified by live SMS on the same BridgeEscrow account. The hosted page requests M-PESA payment to that verified number.</li>
      <li>A request or prompt does not mean payment succeeded. After provider callback checks and status verification, funds enter escrow and your server receives escrow.held.</li>
      <li>After delivery, the buyer confirms receipt or shares their delivery code. Your server receives escrow.released and your Available Balance increases by the amount after fees. Disputes keep funds held for administrator resolution.</li>
    </ol>
    <p className="text-sm text-amber-200">These keys can request real payments. Card processing is not configured. Keep sandbox keys, examples and balances separate.</p>
    <div className="flex gap-2" aria-label="Example language">{Object.keys(snippets).map((value) => <button key={value} onClick={() => setLanguage(value)} type="button" aria-pressed={language === value} className="rounded-lg bg-navy-900 px-3 py-2 text-xs text-teal-300">{value}</button>)}</div>
    <pre className="max-h-[480px] overflow-auto rounded-xl bg-navy-900 p-4 text-[11px] text-slate-300"><code>{snippets[language]}</code></pre>
    <WebhookGuide />
  </section>
}
