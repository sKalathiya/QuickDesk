import { useState } from "react";
import { Link, useParams } from "react-router";

import { Alert } from "../../../components/ui/Alert";
import { Badge } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";

import { useAgentTicketDetail } from "../hooks/useAgentTicketDetail";

import TicketClassificationForm from "../components/TicketClassificationForm";
import TicketAuditLogs from "../components/TicketAuditLogs";
import ResolveTicketModal from "../components/ResolveTicketModal";

function formatDate(value: string | null) {
  if (!value) return "Not available";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function AgentTicketDetailPage() {
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);

  const { ticketId } = useParams<{ ticketId: string }>();

  const {
    data: ticket,
    isPending,
    isError,
    error,
    refetch,
  } = useAgentTicketDetail(ticketId ?? "");

  if (!ticketId) {
    return (
      <Alert tone="danger" title="Invalid ticket">
        The ticket ID is missing.
      </Alert>
    );
  }

  if (isPending) {
    return (
      <p role="status" className="p-6 text-sm text-muted">
        Loading ticket details...
      </p>
    );
  }

  if (isError) {
    return (
      <div className="space-y-4">
        <Alert tone="danger" title="Unable to load ticket">
          {error.message}
        </Alert>

        <Button variant="secondary" onClick={() => void refetch()}>
          Try again
        </Button>
      </div>
    );
  }

  if (!ticket) return null;

  const isResolved = ticket.status === "RESOLVED";

  const hasAIResponse = Boolean(ticket.ai_resolution_description?.trim());

  const hasFinalResolution = Boolean(ticket.resolutionDescription?.trim());

  return (
    <div className="w-full space-y-6">
      {/* Back navigation */}
      <Link
        to="/agent"
        className="inline-flex text-sm font-medium text-brand hover:underline"
      >
        ← Back to Tickets
      </Link>

      {/* Page Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="break-words text-2xl font-semibold tracking-tight text-foreground">
              {ticket.title}
            </h1>

            <Badge tone={isResolved ? "resolved" : "open"}>
              {isResolved ? "Resolved" : "Open"}
            </Badge>
          </div>

          <p className="break-all font-mono text-xs text-subtle">
            Ticket ID: {ticket.id}
          </p>
        </div>

        <Button
          type="button"
          variant="primary"
          disabled={isResolved}
          onClick={() => setIsResolveModalOpen(true)}
        >
          {isResolved ? "Resolved" : "Resolve Ticket"}
        </Button>
      </header>

      {/* Original Ticket */}
      <section className="space-y-5 rounded-xl border border-border bg-surface p-5 shadow-xs">
        <div className="space-y-1">
          <h2 className="text-lg font-semibold text-foreground">
            Original Ticket
          </h2>

          <p className="text-sm text-muted">
            Information submitted by the employee.
          </p>
        </div>

        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-1">
            <dt className="text-xs font-medium text-subtle">Status</dt>

            <dd>
              <Badge tone={isResolved ? "resolved" : "open"}>
                {isResolved ? "Resolved" : "Open"}
              </Badge>
            </dd>
          </div>

          <div className="space-y-1">
            <dt className="text-xs font-medium text-subtle">Created on</dt>

            <dd className="text-sm text-foreground">
              {formatDate(ticket.created_at)}
            </dd>
          </div>

          {ticket.fileName && (
            <div className="space-y-1">
              <dt className="text-xs font-medium text-subtle">Filename</dt>

              <dd className="break-all text-sm text-foreground">
                {ticket.fileName}
              </dd>
            </div>
          )}

          {isResolved && ticket.resolved_at && (
            <div className="space-y-1">
              <dt className="text-xs font-medium text-subtle">Resolved on</dt>

              <dd className="text-sm text-foreground">
                {formatDate(ticket.resolved_at)}
              </dd>
            </div>
          )}
        </dl>

        <div className="space-y-2 border-t border-border pt-4">
          <h3 className="text-sm font-semibold text-foreground">Description</h3>

          <p className="whitespace-pre-wrap break-words text-sm leading-6 text-muted">
            {ticket.description}
          </p>
        </div>
      </section>

      {/* AI Response and Final Resolution */}
      {(hasAIResponse || hasFinalResolution) && (
        <section className="space-y-5 rounded-xl border border-border bg-surface p-5 shadow-xs">
          <div className="space-y-1">
            <h2 className="text-lg font-semibold text-foreground">
              Resolution Details
            </h2>

            <p className="text-sm text-muted">
              Compare the original AI-generated reply with the agent's final
              resolution.
            </p>
          </div>

          <div className="grid grid-cols-1 items-start gap-5 lg:grid-cols-2">
            {/* Original AI Response */}
            {hasAIResponse && (
              <div className="min-w-0 space-y-3 rounded-lg border border-brand/25 bg-brand-subtle p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-foreground">
                    AI-Generated Response
                  </h3>

                  <Badge tone="brand">AI Draft</Badge>
                </div>

                <p className="whitespace-pre-wrap break-words text-sm leading-6 text-foreground">
                  {ticket.ai_resolution_description}
                </p>
              </div>
            )}

            {/* Final Resolution */}
            {hasFinalResolution && (
              <div className="min-w-0 space-y-3 rounded-lg border border-status-resolved/25 bg-status-resolved-subtle p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-foreground">
                    Final Resolution
                  </h3>

                  <Badge tone="resolved">Agent Reply</Badge>
                </div>

                <p className="whitespace-pre-wrap break-words text-sm leading-6 text-foreground">
                  {ticket.resolutionDescription}
                </p>

                {isResolved && ticket.resolved_at && (
                  <p className="border-t border-border pt-3 text-xs text-muted">
                    Resolved on {formatDate(ticket.resolved_at)}
                  </p>
                )}
              </div>
            )}
          </div>
        </section>
      )}

      {/* Agent Category and Priority */}
      <TicketClassificationForm ticket={ticket} />

      {/* Ticket Logs - full width, below everything */}
      <TicketAuditLogs ticketId={ticket.id} />

      {/* Resolve Modal */}
      {isResolveModalOpen && !isResolved && (
        <ResolveTicketModal
          ticket={ticket}
          onClose={() => setIsResolveModalOpen(false)}
        />
      )}
    </div>
  );
}
