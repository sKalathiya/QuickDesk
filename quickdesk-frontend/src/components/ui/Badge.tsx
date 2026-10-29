import type { ReactNode } from 'react'
import { cx } from '../../lib/cx'

export type BadgeTone =
  | 'neutral'
  | 'brand'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'open'
  | 'resolved'
  | 'priority-low'
  | 'priority-medium'
  | 'priority-high'
  | 'category-it'
  | 'category-hr'
  | 'category-finance'
  | 'category-admin'

const tones: Record<BadgeTone, string> = {
  neutral: 'border-border bg-surface-muted text-muted',
  brand: 'border-brand/25 bg-brand-subtle text-brand-muted',
  success: 'border-success/25 bg-success-subtle text-success',
  warning: 'border-warning/25 bg-warning-subtle text-warning',
  danger: 'border-danger/25 bg-danger-subtle text-danger',
  info: 'border-info/25 bg-info-subtle text-info',
  open: 'border-status-open/25 bg-status-open-subtle text-status-open',
  resolved: 'border-status-resolved/25 bg-status-resolved-subtle text-status-resolved',
  'priority-low': 'border-priority-low/25 bg-priority-low-subtle text-priority-low',
  'priority-medium': 'border-priority-medium/25 bg-priority-medium-subtle text-priority-medium',
  'priority-high': 'border-priority-high/25 bg-priority-high-subtle text-priority-high',
  'category-it': 'border-category-it/25 bg-category-it-subtle text-category-it',
  'category-hr': 'border-category-hr/25 bg-category-hr-subtle text-category-hr',
  'category-finance': 'border-category-finance/25 bg-category-finance-subtle text-category-finance',
  'category-admin': 'border-category-admin/25 bg-category-admin-subtle text-category-admin',
}

export function Badge({ tone = 'neutral', children }: { tone?: BadgeTone; children: ReactNode }) {
  return (
    <span
      className={cx(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium tracking-wide',
        tones[tone],
      )}
    >
      {children}
    </span>
  )
}
