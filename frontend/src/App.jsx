import { Routes, Route, Navigate } from 'react-router-dom'
import Shell from './components/Shell'
import RequireAuth from './components/RequireAuth'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import Dashboard from './pages/Dashboard'
import EscrowList from './pages/EscrowList'
import EscrowDetail from './pages/EscrowDetail'
import PaymentAction from './pages/PaymentAction'
import Withdraw from './pages/Withdraw'
import Deposit from './pages/Deposit'
import PaymentSelection from './pages/protected/PaymentSelection'
import ProtectedNew from './pages/protected/ProtectedNew'
import Reports from './pages/protected/Reports'
import AdminPayment from './pages/protected/AdminPayment'
import AdminPortal from './pages/AdminPortal'
import PhoneChannels from './pages/PhoneChannels'
import Account from './pages/Account'
import DeveloperApi from './pages/developer/DeveloperApi'
import HostedCheckout from './pages/integration/HostedCheckout'
import SellerApi from './pages/integration/SellerApi'

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/account" element={<RequireAuth><Account /></RequireAuth>} />
        <Route path="/phone" element={<RequireAuth><PhoneChannels /></RequireAuth>} />
        <Route path="/developers/api" element={<RequireAuth><DeveloperApi /></RequireAuth>} />
        <Route path="/developers/api/legacy" element={<RequireAuth><SellerApi /></RequireAuth>} />
        <Route path="/seller/api" element={<Navigate to="/developers/api" replace />} />
        <Route path="/checkout/:token" element={<HostedCheckout />} />
        <Route path="/payments/buy" element={<RequireAuth><PaymentSelection /></RequireAuth>} />
        <Route path="/protected/new/:category" element={<RequireAuth><ProtectedNew /></RequireAuth>} />
        <Route path="/merchant/reports" element={<RequireAuth><Reports /></RequireAuth>} />
        <Route path="/admin/payments/:id" element={<RequireAuth><AdminPayment /></RequireAuth>} />
        <Route path="/admin" element={<RequireAuth><AdminPortal /></RequireAuth>} />
        <Route path="/admin/reports" element={<RequireAuth><Reports admin /></RequireAuth>} />
        <Route path="/payments/send" element={<RequireAuth><PaymentAction key="send" mode="send" /></RequireAuth>} />
        <Route path="/wallet/deposit" element={<RequireAuth><Deposit /></RequireAuth>} />
        <Route path="/wallet/withdraw" element={<RequireAuth><Withdraw /></RequireAuth>} />
        <Route path="/escrows" element={<RequireAuth><EscrowList /></RequireAuth>} />
        <Route path="/escrows/received" element={<RequireAuth><EscrowList received /></RequireAuth>} />
        <Route path="/escrows/new" element={<Navigate to="/escrows" replace />} />
        <Route path="/escrows/:id" element={<RequireAuth><EscrowDetail /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  )
}
