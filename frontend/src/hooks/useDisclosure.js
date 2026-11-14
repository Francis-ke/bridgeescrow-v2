import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
export function useDisclosure() {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const location = useLocation()
  useEffect(() => { setOpen(false) }, [location.key])
  useEffect(() => {
    if (!open) return
    function dismiss(event) {
      if (event.type === 'keydown' && event.key === 'Escape') {
        setOpen(false); ref.current?.querySelector('button')?.focus()
      } else if (event.type === 'pointerdown' && !ref.current?.contains(event.target)) setOpen(false)
    }
    document.addEventListener('keydown', dismiss)
    document.addEventListener('pointerdown', dismiss)
    return () => { document.removeEventListener('keydown', dismiss); document.removeEventListener('pointerdown', dismiss) }
  }, [open])
  return { open, setOpen, ref }
}
