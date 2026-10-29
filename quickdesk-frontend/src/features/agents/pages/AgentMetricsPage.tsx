import { Metric } from "../../../components/ui/Metric";
import { Button } from "../../../components/ui/Button";
import { Alert } from "../../../components/ui/Alert";
import { Card } from "../../../components/ui/Card";

import MetricBreakdown from "../components/MetricBreakdown";
import { useAgentMetrics } from "../hooks/useAgentMetrics";

function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) {
    return "N/A";
  }

  if (seconds === 0) {
    return "0 min";
  }

  if (seconds < 60) {
    return `${Math.round(seconds)} sec`;
  }

  if (seconds < 3600) {
    return `${(seconds / 60).toFixed(1)} min`;
  }

  if (seconds < 86400) {
    return `${(seconds / 3600).toFixed(1)} hrs`;
  }

  return `${(seconds / 86400).toFixed(1)} days`;
}

const statusLabels = {
  OPEN: "Open",
  RESOLVED: "Resolved",
} as const;

const categoryLabels = {
  IT: "IT",
  HR: "HR",
  FINANCE: "Finance",
  ADMIN: "Admin",
  OTHER: "Other",
  NOT_SPECIFIED: "Not specified",
} as const;

const priorityLabels = {
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
  NOT_SPECIFIED: "Not specified",
} as const;

export default function AgentMetricsPage() {
  const { data, isPending, isError, error, refetch, isFetching } =
    useAgentMetrics();

  if (isPending) {
    return (
      <div role="status" className="w-full space-y-6">
        <div className="space-y-2">
          <div className="h-8 w-64 animate-pulse rounded-md bg-surface-muted" />
          <div className="h-4 w-80 max-w-full animate-pulse rounded-md bg-surface-muted" />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <div
              key={index}
              aria-hidden="true"
              className="h-32 animate-pulse rounded-xl border border-border bg-surface-muted"
            />
          ))}
        </div>

        <span className="sr-only">Loading dashboard metrics...</span>
      </div>
    );
  }

  if (isError && !data) {
    return (
      <div className="w-full space-y-4">
        <Alert tone="danger" title="Unable to load metrics">
          {error.message}
        </Alert>

        <Button variant="secondary" onClick={() => void refetch()}>
          Try again
        </Button>
      </div>
    );
  }

  if (!data) return null;

  const total = data.total_tickets;
  const open = data.tickets_by_status.OPEN ?? 0;
  const resolved = data.tickets_by_status.RESOLVED ?? 0;

  const resolvedPercentage = total > 0 ? (resolved / total) * 100 : 0;

  const statusItems = Object.entries(statusLabels).map(([key, label]) => ({
    label,
    value: data.tickets_by_status[key as keyof typeof statusLabels] ?? 0,
  }));

  const categoryItems = Object.entries(categoryLabels).map(([key, label]) => ({
    label,
    value: data.tickets_by_category[key as keyof typeof categoryLabels] ?? 0,
  }));

  const priorityItems = Object.entries(priorityLabels).map(([key, label]) => ({
    label,
    value: data.tickets_by_priority[key as keyof typeof priorityLabels] ?? 0,
  }));

  return (
    <div className="w-full space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Metrics Dashboard
          </h1>

          <p className="text-sm text-muted">
            Monitor ticket volumes, resolution performance, and AI
            classification overrides.
          </p>
        </div>

        <Button
          type="button"
          variant="secondary"
          size="md"
          loading={isFetching}
          onClick={() => void refetch()}
        >
          {isFetching ? "Refreshing..." : "Refresh"}
        </Button>
      </header>

      {isError && (
        <Alert tone="warning" title="Refresh failed">
          {error.message}. Showing the last available metrics.
        </Alert>
      )}

      <section
        aria-label="Key performance metrics"
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <Metric
          label="Total Tickets"
          value={total.toLocaleString("en-IN")}
          detail="All submitted support tickets"
        />

        <Metric
          label="Open Tickets"
          value={open.toLocaleString("en-IN")}
          detail="Awaiting resolution"
        />

        <Metric
          label="Resolved Tickets"
          value={resolved.toLocaleString("en-IN")}
          detail={`${resolvedPercentage.toFixed(1)}% of all tickets`}
        />

        <Metric
          label="Median Resolution Time"
          value={
            resolved > 0 ? formatDuration(data.median_resolution_time) : "N/A"
          }
          detail="Median time from creation to resolution"
        />
      </section>

      <section aria-label="AI classification performance" className="space-y-4">
        <h2 className="text-lg font-semibold text-foreground">
          AI Performance
        </h2>

        <Card
          title="AI Category Override Rate"
          description="Percentage of AI-classified tickets whose suggested category was overridden by an agent."
        >
          <div className="space-y-4">
            <div className="flex flex-wrap items-baseline gap-3">
              <p className="text-3xl font-semibold tracking-tight text-foreground">
                {data.agent_overridden_tickets_percentage.toFixed(1)}%
              </p>

              <p className="text-sm text-muted">Category override rate</p>
            </div>

            <div className="h-3 overflow-hidden rounded-full bg-canvas-subtle">
              <div
                className="h-full rounded-full bg-brand transition-[width] duration-300"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(0, data.agent_overridden_tickets_percentage),
                  )}%`,
                }}
              />
            </div>

            <p className="text-xs text-subtle">
              Based on the backend's recorded AI category override metric.
            </p>
          </div>
        </Card>
      </section>

      <section aria-label="Ticket breakdowns" className="space-y-4">
        <h2 className="text-lg font-semibold text-foreground">
          Ticket Breakdown
        </h2>

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
          <MetricBreakdown
            title="Tickets by Status"
            description="Distribution of open and resolved tickets."
            items={statusItems}
            total={total}
          />

          <MetricBreakdown
            title="Tickets by Priority"
            description="Distribution by currently saved priority."
            items={priorityItems}
            total={total}
          />

          <div className="lg:col-span-2">
            <MetricBreakdown
              title="Tickets by Category"
              description="Distribution by currently saved category."
              items={categoryItems}
              total={total}
            />
          </div>
        </div>
      </section>
    </div>
  );
}
