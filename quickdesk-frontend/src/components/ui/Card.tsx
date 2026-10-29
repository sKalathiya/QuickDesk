import type { ReactNode } from 'react'
import { cx } from '../../lib/cx'

type CardProps = {
  title?: string
  description?: string
  actions?: ReactNode
  children: ReactNode
  className?: string
}

export function Card({ title, description, actions, children, className }: CardProps) {
  const hasHeader = Boolean(title || description || actions)

  return (
    <section className={cx('rounded-xl border border-border bg-surface shadow-sm', className)}>
      {hasHeader ? (
        <header className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>
            {title ? (
              <h3 className="text-base font-semibold tracking-tight text-foreground">{title}</h3>
            ) : null}
            {description ? <p className="mt-1 text-sm text-muted">{description}</p> : null}
          </div>
          {actions}
        </header>
      ) : null}
      <div className={cx(hasHeader ? 'px-5 py-4' : 'p-5')}>{children}</div>
    </section>
  )
}
