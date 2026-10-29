import { Alert } from "../../../components/ui/Alert";
import { Button } from "../../../components/ui/Button";
import { Badge } from "../../../components/ui/Badge";

import { useTicketAuditLogs } from "../hooks/useAgentTicketDetail";

const logLabels = {
  CATEGORY_CHANGE: "Category changed",
  PRIORITY_CHANGE: "Priority changed",
  RESOLUTION_DESCRIPTION_CHANGE: "Resolution updated",
};

function formatValue(value: string | null) {
  if (!value || value === "None") return "Not specified";

  if (value === "NOT_SPECIFIED") return "Not specified";

  if (value.length > 100) return value;

  return value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function TicketAuditLogs({ ticketId }: { ticketId: string }) {
  const {
    data: logs,
    isPending,
    isError,
    error,
    refetch,
  } = useTicketAuditLogs(ticketId);

  return (
    <section className="space-y-5 rounded-xl border border-border bg-surface p-5 shadow-xs">
      <div>
        <h2 className="text-lg font-semibold text-foreground">
          Ticket History
        </h2>
        <p className="mt-1 text-sm text-muted">
          Changes made by support agents.
        </p>
      </div>

      {isPending && (
        <p role="status" className="text-sm text-muted">
          Loading ticket history...
        </p>
      )}

      {isError && (
        <div className="space-y-3">
          <Alert tone="danger" title="Unable to load history">
            {error.message}
          </Alert>
          <Button variant="secondary" size="sm" onClick={() => void refetch()}>
            Try again
          </Button>
        </div>
      )}

      {!isPending && !isError && logs?.length === 0 && (
        <p className="rounded-lg bg-surface-muted p-4 text-sm text-muted">
          No changes have been recorded for this ticket.
        </p>
      )}

      {!isPending && !isError && logs && logs.length > 0 && (
        <ol className="space-y-4">
          {[...logs]
            .sort(
              (a, b) =>
                new Date(b.created_at).getTime() -
                new Date(a.created_at).getTime(),
            )
            .map((log) => (
              <li
                key={log.id}
                className="space-y-3 rounded-lg border border-border p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-foreground">
                    {logLabels[log.log_type]}
                  </p>
                  <time
                    dateTime={log.created_at}
                    className="text-xs text-subtle"
                  >
                    {formatDate(log.created_at)}
                  </time>
                </div>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <div className="space-y-1 rounded-md bg-surface-muted p-3">
                    <p className="text-xs text-subtle">Previous value</p>
                    <p className="whitespace-pre-wrap break-words text-sm text-foreground">
                      {formatValue(log.old_value)}
                    </p>
                  </div>

                  <div className="space-y-1 rounded-md bg-surface-muted p-3">
                    <p className="text-xs text-subtle">New value</p>
                    <p className="whitespace-pre-wrap break-words text-sm text-foreground">
                      {formatValue(log.new_value)}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone="neutral">Agent</Badge>
                  <span className="break-all font-mono text-xs text-subtle">
                    {log.agent_id}
                  </span>
                </div>
              </li>
            ))}
        </ol>
      )}
    </section>
  );
}
