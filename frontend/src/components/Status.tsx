import type { ReactNode } from 'react'
import { AlertTriangle, Inbox, LoaderCircle, RotateCcw } from 'lucide-react'

export function PageLoader({ rows = 5 }: { rows?: number }) {
  return (
    <div className="skeleton-stack" aria-label="Loading content" aria-busy="true">
      {Array.from({ length: rows }, (_, index) => <div className="skeleton-row" key={index} />)}
    </div>
  )
}

export function InlineLoader({ label = 'Working' }: { label?: string }) {
  return <span className="inline-loader"><LoaderCircle size={15} className="spin" aria-hidden="true" />{label}</span>
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="state-panel state-error" role="alert">
      <AlertTriangle size={20} aria-hidden="true" />
      <div><strong>Something went wrong</strong><p>{message}</p></div>
      {onRetry && <button className="button button-secondary" onClick={onRetry}><RotateCcw size={15} />Retry</button>}
    </div>
  )
}

export function EmptyState({ title, message, action }: { title: string; message: string; action?: ReactNode }) {
  return (
    <div className="empty-state">
      <Inbox size={24} aria-hidden="true" />
      <strong>{title}</strong>
      <p>{message}</p>
      {action}
    </div>
  )
}

export function StatusTag({ value }: { value: string }) {
  return <span className={`status status-${value.replace('_', '-')}`}>{value.replace('_', ' ')}</span>
}
