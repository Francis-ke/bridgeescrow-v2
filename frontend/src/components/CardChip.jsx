import { useId } from 'react'

export default function CardChip() {
  const id = useId().replace(/:/g, '')

  return (
    <svg viewBox="0 0 56 42" aria-hidden="true"
      className="h-8 w-11 shrink-0 drop-shadow-[0_1px_2px_rgba(0,0,0,0.35)]">
      <defs>
        <linearGradient id={`${id}-gold`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#a77a28" />
          <stop offset="0.23" stopColor="#f5dfa0" />
          <stop offset="0.48" stopColor="#c69e48" />
          <stop offset="0.7" stopColor="#f8e8b7" />
          <stop offset="1" stopColor="#b58a37" />
        </linearGradient>
        <pattern id={`${id}-grain`} width="3" height="3" patternUnits="userSpaceOnUse">
          <path d="M0 .5H3" stroke="#fff8d9" strokeOpacity=".16" strokeWidth=".5" />
        </pattern>
      </defs>
      <rect x=".75" y=".75" width="54.5" height="40.5" rx="7"
        fill={`url(#${id}-gold)`} stroke="#856326" strokeWidth="1.5" />
      <rect x="2" y="2" width="52" height="38" rx="6"
        fill={`url(#${id}-grain)`} stroke="#fff3c7" strokeOpacity=".6" strokeWidth=".6" />
      <g fill="none" stroke="#806126" strokeWidth="1" strokeLinejoin="round">
        <rect x="18" y="11" width="20" height="20" rx="4" />
        <path d="M18 15H1M18 27H1M38 15H55M38 27H55
          M21 12L15 6V1M35 12L41 6V1M21 30L15 36V41M35 30L41 36V41
          M1 21H18M38 21H55" />
      </g>
      <path d="M7 3H48" stroke="#fff7d9" strokeOpacity=".7" strokeLinecap="round" />
    </svg>
  )
}
