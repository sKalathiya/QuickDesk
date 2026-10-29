import type { ButtonHTMLAttributes } from 'react'
import { cx } from '../../lib/cx'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
  size?: Size
  loading?: boolean
}

const variants: Record<Variant, string> = {
  primary:
    'border-transparent bg-brand text-brand-foreground hover:bg-brand-hover active:bg-brand-active',
  secondary:
    'border-border-strong bg-surface text-foreground hover:bg-surface-muted active:bg-canvas-subtle',
  ghost:
    'border-transparent bg-transparent text-foreground hover:bg-surface-muted active:bg-canvas-subtle',
  danger:
    'border-transparent bg-danger text-danger-foreground hover:bg-danger-hover active:bg-danger-hover',
}

const sizes: Record<Size, string> = {
  sm: 'h-8 gap-1.5 px-3 text-xs',
  md: 'h-10 gap-2 px-4 text-sm',
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className,
  children,
  type = 'button',
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading

  return (
    <button
      type={type}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      className={cx(
        'inline-flex items-center justify-center rounded-md border font-medium transition-colors duration-150 ease-out',
        'cursor-pointer disabled:cursor-not-allowed disabled:border-border disabled:bg-surface-muted disabled:text-subtle',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <span
          aria-hidden="true"
          className="size-3.5 animate-spin rounded-full border-2 border-current border-r-transparent"
        />
      ) : null}
      {children}
    </button>
  )
}
