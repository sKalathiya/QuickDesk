export function Metric({
  label,
  value,
  detail,
}: {
  label: string
  value: string
  detail?: string
}) {
  return (
    <div className="rounded-xl border border-border bg-surface px-5 py-4 shadow-xs">
      <p className="text-xs font-medium tracking-wide text-subtle uppercase">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-tight text-foreground">{value}</p>
      {detail ? <p className="mt-1 text-xs text-muted">{detail}</p> : null}
    </div>
  )
}
