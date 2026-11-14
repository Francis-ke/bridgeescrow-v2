import { useDisclosure } from '../hooks/useDisclosure'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui'
import NotificationBell from './NotificationBell'
import BackButton from './BackButton'

export default function Shell({ children }) {
  const { user, signOut } = useAuth()
  const { open, setOpen, ref: menu } = useDisclosure()
  const navigate = useNavigate()
  const links = user
    ? [['/', 'Home'], ['/escrows', 'My escrows'], ['/developers/api', 'Developer API'], ['/phone', 'Phone & USSD']]
    : [['/login', 'Sign in'], ['/register', 'Create account']]

  if (user?.role === 'admin' && !links.some(([path]) => path === '/admin/reports')) links.push(['/admin', 'Administrator portal'])
  if (user?.role === 'merchant' && !links.some(([path]) => path === '/merchant/reports')) links.push(['/merchant/reports', 'Merchant reports'])

  function logout() {
    setOpen(false)
    signOut()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-navy-900 text-white">
      <header className="border-b border-white/10 bg-navy-800/60">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <Link to="/" className="font-bold text-teal-400">BridgeEscrow</Link>
          <div className="flex items-center gap-3">
          {user && <NotificationBell key={user.id} />}
          <div className="relative" ref={menu}>
            <Button variant="ghost" aria-label={open ? 'Close navigation' : 'Open navigation'}
              aria-expanded={open} aria-controls="site-navigation" onClick={() => setOpen(!open)}
              className="flex h-10 w-10 items-center justify-center px-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-400">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"
                stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                <path d={open ? 'M6 6l12 12M6 18L18 6' : 'M4 6h16M4 12h16M4 18h16'} />
              </svg>
            </Button>
            {open && <nav id="site-navigation" aria-label="Main navigation"
              className="absolute right-0 top-full z-50 mt-3 w-64 max-w-[calc(100vw-2rem)] rounded-xl border border-white/10 bg-navy-800 p-2 shadow-xl">
              {links.map(([to, label]) => <NavLink key={to} to={to} end onClick={() => setOpen(false)}
                className={({ isActive }) => `block rounded-lg px-4 py-3 text-sm transition hover:bg-white/5 focus-visible:outline focus-visible:outline-teal-400 ${isActive ? 'bg-teal-400/10 text-teal-300' : 'text-slate-200'}`}>
                {label}
              </NavLink>)}
              {user && <button type="button" onClick={logout}
                className="mt-2 w-full border-t border-white/10 px-4 py-3 text-left text-sm text-slate-300 hover:text-white">
                Sign out
              </button>}
            </nav>}
          </div>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        <BackButton />
        {children}
      </main>
    </div>
  )
}
