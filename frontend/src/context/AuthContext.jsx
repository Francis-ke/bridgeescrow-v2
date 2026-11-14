import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { auth } from '../api/endpoints'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    let sessionToken = localStorage.getItem('be_token')
    const expired = () => { localStorage.removeItem('be_token'); setUser(null) }
    window.addEventListener('session-expired', expired)
    async function restore() {
      sessionToken = localStorage.getItem('be_token')
      const restoring = sessionToken
      setUser(null); setLoading(true)
      try {
        if (restoring) {
          const data = await auth.me()
          if (active && restoring === localStorage.getItem('be_token')) setUser(data.user)
        }
      } catch (error) {
        if (active && [401, 403].includes(error.status) &&
            restoring === localStorage.getItem('be_token')) expired()
      } finally {
        if (active && restoring === localStorage.getItem('be_token')) setLoading(false)
        else if (active && !localStorage.getItem('be_token')) setLoading(false)
      }
    }
    const changed = (event) => { if (event.key === 'be_token' || event.key === null) restore() }
    window.addEventListener('storage', changed)
    restore()
    return () => {
      active = false; window.removeEventListener('session-expired', expired)
      window.removeEventListener('storage', changed)
    }
  }, [])

  useEffect(() => {
    if (!user?.id || (user.card_number && user.card_cvv)) return
    let active = true
    auth.me().then(({ user: profile }) => { if (active) setUser(profile) }).catch(() => {})
    return () => { active = false }
  }, [user?.id, user?.card_number, user?.card_cvv])

  function signIn(session) {
    localStorage.setItem('be_token', session.token)
    setUser(session.user); setLoading(false)
  }

  function signOut() {
    localStorage.removeItem('be_token')
    setUser(null); setLoading(false)
  }

  const value = useMemo(() => ({ user, loading, signIn, signOut, updateUser: setUser }), [user, loading])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)
