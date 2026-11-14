import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { notifications } from '../api/endpoints'
export function useNotifications(open) {
  const [items, setItems] = useState([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [refresh, setRefresh] = useState(0)
  const location = useLocation()
  useEffect(() => {
    let active = true
    async function load() {
      try {
        const data = await notifications.list()
        if (active) { setItems(data.notifications); setCount(Number(data.unread_count) || 0); setError('') }
      } catch { if (active) setError('Could not load notifications. Please try again.') }
      finally { if (active) setLoading(false) }
    }
    load()
    const interval = setInterval(load, 10000)
    window.addEventListener('focus', load)
    window.addEventListener('account-updated', load)
    return () => {
      active = false; clearInterval(interval)
      window.removeEventListener('focus', load)
      window.removeEventListener('account-updated', load)
    }
  }, [open, location.key, refresh])
  async function mutate(request, update) {
    if (busy) return false
    setBusy(true); setError('')
    try { await request(); update(); return true }
    catch (err) { setError(err.message); return false } finally { setBusy(false) }
  }
  const read = (item) => item.read ? Promise.resolve(true) : mutate(() => notifications.read(item.id), () => {
    setCount((value) => Math.max(0, value - 1))
    setItems((current) => current.map((row) => row.id === item.id ? { ...row, read: true } : row))
  })
  const readAll = () => mutate(() => notifications.readAll(), () => {
    setItems((current) => current.map((item) => ({ ...item, read: true }))); setCount(0)
  })
  const retry = () => { setLoading(true); setRefresh((value) => value + 1) }
  return { items, count, loading, busy, error, read, readAll, retry }
}
