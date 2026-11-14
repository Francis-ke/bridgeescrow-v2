import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <p className="p-10 text-center text-slate-400">Loading…</p>
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}
