import type React from 'react'
import s from './Button.module.css'

interface Props {
    children: React.ReactNode
    variant: 'primary' | 'ghost'
    compact?: boolean
}

export default function Button({ children, variant, compact }: Props) {
  const className = [
    s.button,
    s[variant],
    compact && s.compact,
  ].filter(Boolean).join(' ')

  return (
    <button type="button" className={className}>{children}</button>
  )
}
