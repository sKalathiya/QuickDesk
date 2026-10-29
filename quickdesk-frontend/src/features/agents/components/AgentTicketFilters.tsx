import { Button } from "../../../components/ui/Button";
import { TextField, SelectField } from "../../../components/ui/TextField";

import type { AgentTicketFilters as Filters } from "../api/agentApi";

type Props = {
  filters: Filters;
  onChange: (filters: Filters) => void;
};

export default function AgentTicketFilters({ filters, onChange }: Props) {
  const update = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="space-y-4 rounded-xl border border-border bg-surface p-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <TextField
          id="ticket-search"
          label="Search by title"
          placeholder="Search tickets..."
          value={filters.title}
          onChange={(event) => update("title", event.target.value)}
        />

        <SelectField
          id="ticket-status"
          label="Status"
          value={filters.status}
          onChange={(event) =>
            update("status", event.target.value as Filters["status"])
          }
        >
          <option value="">All statuses</option>
          <option value="OPEN">Open</option>
          <option value="RESOLVED">Resolved</option>
        </SelectField>

        <SelectField
          id="ticket-category"
          label="Category"
          value={filters.category}
          onChange={(event) =>
            update("category", event.target.value as Filters["category"])
          }
        >
          <option value="">All categories</option>
          <option value="IT">IT</option>
          <option value="HR">HR</option>
          <option value="FINANCE">Finance</option>
          <option value="ADMIN">Admin</option>
          <option value="OTHER">Other</option>
          <option value="NOT_SPECIFIED">Not specified</option>
        </SelectField>

        <SelectField
          id="ticket-priority"
          label="Priority"
          value={filters.priority}
          onChange={(event) =>
            update("priority", event.target.value as Filters["priority"])
          }
        >
          <option value="">All priorities</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="NOT_SPECIFIED">Not specified</option>
        </SelectField>
      </div>

      <div className="flex justify-end">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={() =>
            onChange({
              status: "",
              category: "",
              priority: "",
              title: "",
            })
          }
        >
          Clear filters
        </Button>
      </div>
    </div>
  );
}
