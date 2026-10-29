import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'
import { cx } from '../../lib/cx'

type FieldProps = {
  id: string
  label: string
  hint?: string
  error?: string
}

const control =
  'w-full rounded-md border border-border bg-surface px-3 text-sm text-foreground shadow-xs transition-colors duration-150 placeholder:text-subtle hover:border-border-strong disabled:cursor-not-allowed disabled:bg-surface-muted disabled:text-subtle aria-invalid:border-danger aria-invalid:focus-visible:outline-danger'

function Field({
  id,
  label,
  hint,
  error,
  children,
}: FieldProps & { children: ReactNode }) {
  const messageId = error ? `${id}-error` : hint ? `${id}-hint` : undefined

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-foreground">
        {label}
      </label>
      {children}
      {error ? (
        <p id={messageId} className="text-xs text-danger">
          {error}
        </p>
      ) : hint ? (
        <p id={messageId} className="text-xs text-subtle">
          {hint}
        </p>
      ) : null}
    </div>
  )
}

function describedBy(id: string, hint?: string, error?: string) {
  if (error) return `${id}-error`
  if (hint) return `${id}-hint`
  return undefined
}

export function TextField({
  id,
  label,
  hint,
  error,
  className,
  ...props
}: FieldProps & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <Field id={id} label={label} hint={hint} error={error}>
      <input
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(id, hint, error)}
        className={cx(control, 'h-10', className)}
        {...props}
      />
    </Field>
  )
}

export function TextArea({
  id,
  label,
  hint,
  error,
  className,
  ...props
}: FieldProps & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <Field id={id} label={label} hint={hint} error={error}>
      <textarea
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(id, hint, error)}
        className={cx(control, 'min-h-28 py-2', className)}
        {...props}
      />
    </Field>
  )
}

export function SelectField({
  id,
  label,
  hint,
  error,
  className,
  children,
  ...props
}: FieldProps & SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <Field id={id} label={label} hint={hint} error={error}>
      <select
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(id, hint, error)}
        className={cx(control, 'h-10', className)}
        {...props}
      >
        {children}
      </select>
    </Field>
  )
}
