import { useEffect, useState } from "react";

import { Button } from "../../../components/ui/Button";
import { Badge } from "../../../components/ui/Badge";
import { Alert } from "../../../components/ui/Alert";
import { SelectField } from "../../../components/ui/TextField";

import type {
  Ticket,
  TicketCategory,
  TicketPriority,
} from "../../employe/types";

import { useUpdateAgentTicket } from "../hooks/useUpdateAgentTicket";

type Props = {
  ticket: Ticket;
};

function label(value: string): string {
  if (value === "NOT_SPECIFIED") return "Not specified";

  return value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function TicketClassificationForm({ ticket }: Props) {
  const [category, setCategory] = useState<TicketCategory>(ticket.category);

  const [priority, setPriority] = useState<TicketPriority>(ticket.priority);

  const [success, setSuccess] = useState(false);

  const mutation = useUpdateAgentTicket(ticket.id);

  useEffect(() => {
    setCategory(ticket.category);
    setPriority(ticket.priority);
  }, [ticket.category, ticket.priority, ticket.id]);

  const hasChanges =
    category !== ticket.category || priority !== ticket.priority;

  async function handleSave() {
    setSuccess(false);
    mutation.reset();

    try {
      await mutation.mutateAsync({
        category,
        priority,
      });

      setSuccess(true);
    } catch {
      // Display mutation error below.
    }
  }

  return (
    <section className="space-y-6 rounded-xl border border-border bg-surface p-5 shadow-xs">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold text-foreground">
          Classification
        </h2>
        <p className="text-sm text-muted">
          Review the AI suggestions and save the correct category and priority.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-2 rounded-lg bg-brand-subtle p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-brand-muted">
            AI-suggested category
          </p>
          <Badge tone="brand">{label(ticket.ai_category)}</Badge>
        </div>

        <div className="space-y-2 rounded-lg bg-brand-subtle p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-brand-muted">
            AI-suggested priority
          </p>
          <Badge tone="brand">{label(ticket.ai_priority)}</Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <SelectField
          id="agent-ticket-category"
          label="Current category"
          value={category}
          disabled={mutation.isPending || ticket.status === "RESOLVED"}
          onChange={(event) => {
            setSuccess(false);
            setCategory(event.target.value as TicketCategory);
          }}
        >
          {category === "NOT_SPECIFIED" && (
            <option value="NOT_SPECIFIED">Not specified</option>
          )}
          <option value="IT">IT</option>
          <option value="HR">HR</option>
          <option value="FINANCE">Finance</option>
          <option value="ADMIN">Admin</option>
          <option value="OTHER">Other</option>
        </SelectField>

        <SelectField
          id="agent-ticket-priority"
          label="Current priority"
          value={priority}
          disabled={mutation.isPending || ticket.status === "RESOLVED"}
          onChange={(event) => {
            setSuccess(false);
            setPriority(event.target.value as TicketPriority);
          }}
        >
          {priority === "NOT_SPECIFIED" && (
            <option value="NOT_SPECIFIED">Not specified</option>
          )}
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
        </SelectField>
      </div>

      {mutation.isError && (
        <Alert tone="danger" title="Unable to save changes">
          {mutation.error.message}
        </Alert>
      )}

      {success && (
        <Alert tone="success" title="Changes saved">
          Ticket classification has been updated.
        </Alert>
      )}

      <div className="flex justify-end">
        <Button
          type="button"
          loading={mutation.isPending}
          disabled={
            !hasChanges || ticket.status === "RESOLVED" || mutation.isPending
          }
          onClick={() => void handleSave()}
        >
          Save Changes
        </Button>
      </div>
    </section>
  );
}
