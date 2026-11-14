import { useParams } from 'react-router-dom'
import ProtectedDetail from './ProtectedDetail'
export default function AdminPayment() {
  const { id } = useParams()
  return <ProtectedDetail id={id} admin />
}
