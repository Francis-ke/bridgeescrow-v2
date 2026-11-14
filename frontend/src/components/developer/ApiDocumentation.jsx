import { useState } from 'react'
import { examples } from './examples'
import LiveApiDocumentation from './LiveApiDocumentation'
import WebhookGuide from './WebhookGuide'
export default function ApiDocumentation({ application }) {
  const [language, setLanguage] = useState('cURL')
  const snippets = examples(window.location.origin)
  if (application?.environment === 'production') return <LiveApiDocumentation />
  return <section className="space-y-5 rounded-2xl border border-white/10 bg-navy-800/60 p-5">
    <h2 className="text-lg font-semibold">API Documentation</h2>
    <ol className="list-inside list-decimal space-y-2 text-sm text-slate-400">
      <li>Create a sandbox application, then generate credentials with only the permissions your server needs.</li>
      <li>Save the secret key in your server's environment. Send it as <code className="text-teal-300">Authorization: Bearer …</code>.</li>
      <li>Create an escrow from the shop's bill and initiate a card or M-PESA checkout session.</li>
      <li>Redirect the buyer to the returned hosted URL. The buyer verifies email, reviews the immutable total, and confirms payment.</li>
      <li>Use status requests and signed webhooks to track held funds, disputes and buyer-authorized release.</li>
    </ol>
    <div className="flex gap-2" aria-label="Example language">{Object.keys(snippets).map((value) => <button type="button" key={value}
      aria-pressed={language === value} onClick={() => setLanguage(value)}
      className={`rounded-lg px-3 py-2 text-xs ${language === value ? 'bg-teal-400/15 text-teal-300' : 'bg-navy-900 text-slate-400'}`}>{value}</button>)}</div>
    <pre className="max-h-[480px] overflow-auto rounded-xl border border-white/10 bg-navy-900 p-4 text-[11px] leading-relaxed text-slate-300"><code>{snippets[language]}</code></pre>
    <div className="grid gap-4 text-xs leading-relaxed text-slate-400 sm:grid-cols-2">
      <div className="rounded-xl bg-navy-900/50 p-4"><h3 className="mb-2 font-semibold text-slate-200">M-PESA STK Push</h3><p>Use method <code className="text-teal-300">mpesa</code> with phone_number. The current sandbox simulates the flow; it does not send a live STK Push or contact Safaricom.</p></div>
      <div className="rounded-xl bg-navy-900/50 p-4"><h3 className="mb-2 font-semibold text-slate-200">Visa / Mastercard checkout</h3><p>Use method <code className="text-teal-300">card</code>. Hosted checkout displays the card-entry form; current processing is simulated. Raw card numbers and CVCs are not submitted or stored.</p></div>
    </div>
    <details className="rounded-xl border border-white/10 p-4"><summary className="cursor-pointer text-sm font-medium text-teal-300">Disputes and release requests</summary>
      <div className="mt-3 space-y-2 text-xs text-slate-400">
        <p><code className="text-teal-200">POST /api/v1/escrows/{'{id}'}/disputes</code> with <code>{`{ "reason": "Explain the issue in detail" }`}</code> opens a dispute for the application-owned escrow.</p>
        <p><code className="text-teal-200">POST /api/v1/escrows/{'{id}'}/release-requests</code> requests buyer-authorized release; it never directly releases funds. Disputed funds require administrator resolution.</p>
        <p>Live financial operations remain disabled. Sandbox keys cannot access another application's resources or your normal wallet balance.</p>
      </div>
    </details>
    <WebhookGuide />
  </section>
}
