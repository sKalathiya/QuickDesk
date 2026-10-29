import { Badge } from "../../../components/ui/Badge";
import type { BadgeTone } from "../../../components/ui/Badge";
import type { Ticket, TicketCategory, TicketPriority } from "../types";

type TicketCardProps = {
  ticket: Ticket;
};

function resolveValue<T extends string>(
  selected: T,
  aiSuggested: T,
): { value: T; isAI: boolean } {
  if (selected !== "NOT_SPECIFIED") {
    return { value: selected, isAI: false };
  }

  if (aiSuggested !== "NOT_SPECIFIED") {
    return { value: aiSuggested, isAI: true };
  }

  return { value: selected, isAI: false };
}

function formatValue(value: string): string {
  if (value === "NOT_SPECIFIED") {
    return "Not specified";
  }

  return value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(date: string): string {
  const parsed = new Date(date);

  if (Number.isNaN(parsed.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(parsed);
}

const categoryTones: Record<TicketCategory, BadgeTone> = {
  IT: "category-it",
  HR: "category-hr",
  FINANCE: "category-finance",
  ADMIN: "category-admin",
  OTHER: "neutral",
  NOT_SPECIFIED: "neutral",
};

const priorityTones: Record<TicketPriority, BadgeTone> = {
  LOW: "priority-low",
  MEDIUM: "priority-medium",
  HIGH: "priority-high",
  NOT_SPECIFIED: "neutral",
};

export default function TicketCard({ ticket }: TicketCardProps) {
  const category = resolveValue(ticket.category, ticket.ai_category);

  const priority = resolveValue(ticket.priority, ticket.ai_priority);

  const isResolved = ticket.status === "RESOLVED";

  return (
    <article className="flex h-full min-w-0 flex-col rounded-xl border border-border bg-surface p-5 shadow-xs transition-shadow hover:shadow-sm">
      {/* Title and Status */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="min-w-0 break-words text-base font-semibold text-foreground">
          {ticket.title}
        </h3>

        <Badge tone={isResolved ? "resolved" : "open"}>
          {formatValue(ticket.status)}
        </Badge>
      </div>

      {/* Ticket Description */}
      <p className="mt-3 line-clamp-3 whitespace-pre-wrap break-words text-sm leading-6 text-muted">
        {ticket.description}
      </p>

      {/* Filename - only when provided */}
      {ticket.fileName && (
        <div className="mt-4 space-y-1">
          <p className="text-xs font-medium uppercase tracking-wide text-subtle">
            Filename
          </p>

          <p className="break-all text-sm text-foreground">{ticket.fileName}</p>
        </div>
      )}

      {/* Category and Priority */}
      <div className="mt-5 space-y-4 border-t border-border pt-4">
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-subtle">
            Category
          </p>

          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={categoryTones[category.value]}>
              {formatValue(category.value)}
            </Badge>

            {category.isAI && <Badge tone="brand">AI specified</Badge>}
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-subtle">
            Priority
          </p>

          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={priorityTones[priority.value]}>
              {formatValue(priority.value)}
            </Badge>

            {priority.isAI && <Badge tone="brand">AI specified</Badge>}
          </div>
        </div>
      </div>

      {/* Resolution details - only for resolved tickets */}
      {isResolved && (
        <div className="mt-5 space-y-3 rounded-lg border border-status-resolved/25 bg-status-resolved-subtle p-4">
          <h4 className="text-sm font-semibold text-status-resolved">
            Resolution Details
          </h4>

          {ticket.resolutionDescription && (
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted">Resolution</p>

              <p className="whitespace-pre-wrap break-words text-sm leading-6 text-foreground">
                {ticket.resolutionDescription}
              </p>
            </div>
          )}

          {ticket.resolved_at && (
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted">Resolved on</p>

              <p className="text-sm font-medium text-foreground">
                {formatDate(ticket.resolved_at)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Created Date */}
      <div className="mt-auto pt-5">
        <p className="border-t border-border pt-4 text-xs text-subtle">
          Created on {formatDate(ticket.created_at)}
        </p>
      </div>
    </article>
  );
}
