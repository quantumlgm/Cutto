import type React from 'react'
import s from './Button.module.css'

interface Props {
  children: React.ReactNode
  variant: 'primary' | 'ghost'
  compact?: boolean
  onClick?: () => void; 
  disabled?: boolean;
}

export default function Button({ children, variant, compact, onClick, disabled }: Props) {
  const className = [
    s.button,
    s[variant],
    compact && s.compact,
  ].filter(Boolean).join(' ')

  return (
    <button 
      type="button" 
      className={className} 
      onClick={onClick}  
      disabled={disabled} 
    >
      {children}
    </button>
  )
}