import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { wallet } from '../api/endpoints'

export function useWalletOverview(userId) {
  const location = useLocation()
  const [balances, setBalances] = useState(null)
  const [entries, setEntries] = useState(null)
  const [showStatements, setShowStatements] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    function loadBalances() {
      if (showStatements) wallet.ledger().then(({ entries: value }) => {
        if (active) setEntries(value)
      }).catch((err) => { if (active) setError(err.message) })
      wallet.get().then(({ wallet: value }) => { if (active && value.user_id === userId) { setBalances(value); setError('') } })
        .catch((err) => { if (active) setError(err.message) })
    }
    loadBalances()
    const interval = setInterval(loadBalances, 15000)
    window.addEventListener('focus', loadBalances)
    window.addEventListener('account-updated', loadBalances)
    return () => {
      active = false; clearInterval(interval)
      window.removeEventListener('focus', loadBalances)
      window.removeEventListener('account-updated', loadBalances)
    }
  }, [showStatements, userId])

  useEffect(() => {
    if (new URLSearchParams(location.search).get('statements') !== '1') return
    let active = true
    setBusy(true)
    wallet.ledger().then((result) => {
      if (active) { setEntries(result.entries); setShowStatements(true) }
    }).catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setBusy(false) })
    return () => { active = false }
  }, [location.key, location.search])

  useEffect(() => {
    if (showStatements && new URLSearchParams(location.search).get('statements') === '1') {
      document.getElementById('wallet-statements')?.scrollIntoView({ block: 'start' })
    }
  }, [showStatements, entries, location.search])

  async function statements() {
    if (busy) return
    if (showStatements) { setShowStatements(false); return }
    setBusy(true); setError('')
    try {
      const result = await wallet.ledger()
      setEntries(result.entries); setShowStatements(true)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return { balances, entries, showStatements, busy, error, statements }
}
