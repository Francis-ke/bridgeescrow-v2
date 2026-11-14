import { useLocation, useNavigate } from 'react-router-dom'

export default function BackButton() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  if (pathname === '/') return null

  function goBack() {
    if (window.history.state?.idx > 0) {
      navigate(-1)
      return
    }
    const fallback = pathname.startsWith('/escrows/') ? '/escrows'
      : ['/register', '/forgot-password'].includes(pathname) ? '/login' : '/'
    navigate(fallback, { replace: true })
  }

  return (
    <div className="mb-6">
      <button type="button" onClick={goBack} aria-label="Go back"
        className="group inline-flex min-h-11 items-center gap-2.5 rounded-full border border-white/10 bg-navy-800/80 py-1.5 pl-1.5 pr-5 text-sm font-medium text-slate-300 shadow-sm transition hover:border-teal-400/30 hover:bg-teal-400/5 hover:text-teal-300 active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-400">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-400/10 text-teal-400">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
            className="transition-transform motion-safe:group-hover:-translate-x-0.5">
            <path d="m12 5-7 7 7 7M5 12h14" />
          </svg>
        </span>
        Back
      </button>
    </div>
  )
}
