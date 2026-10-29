import type { ReactNode, TdHTMLAttributes, ThHTMLAttributes } from 'react'
import { cx } from '../../lib/cx'

export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-surface shadow-xs">
      <table className="w-full min-w-[40rem] border-collapse text-left text-sm">{children}</table>
    </div>
  )
}

export function THead({ children }: { children: ReactNode }) {
  return <thead className="bg-surface-muted">{children}</thead>
}

export function TBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-border">{children}</tbody>
}

export function Tr({ children }: { children: ReactNode }) {
  return <tr className="hover:bg-canvas-subtle">{children}</tr>
}

export function Th({ className, children, ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cx(
        'px-4 py-3 text-xs font-medium tracking-wide text-subtle uppercase',
        className,
      )}
      {...props}
    >
      {children}
    </th>
  )
}

export function Td({ className, children, ...props }: TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td className={cx('px-4 py-3 text-foreground', className)} {...props}>
      {children}
    </td>
  )
}
