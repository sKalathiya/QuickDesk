import { useEffect, useState } from "react";

import { Alert } from "../../../components/ui/Alert";
import { Badge } from "../../../components/ui/Badge";
import type { BadgeTone } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";

import { Table, THead, TBody, Tr, Th, Td } from "../../../components/ui/Table";

import AgentTicketFilters from "../components/AgentTicketFilters";
import { useAgentTickets } from "../hooks/useAgentTickets";

import type { AgentTicketFilters as Filters } from "../api/agentApi";
import type { TicketCategory, TicketPriority } from "../../employe/types";
import { Link } from "react-router";

const emptyFilters: Filters = {
  status: "",
  category: "",
  priority: "",
  title: "",
};

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

function formatLabel(value: string) {
  if (value === "NOT_SPECIFIED") return "Not specified";

  return value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
  }).format(date);
}

export default function AgentDashboardPage() {
  const [filters, setFilters] = useState<Filters>(emptyFilters);

  const [search, setSearch] = useState("");

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearch(filters.title.trim());
    }, 350);

    return () => window.clearTimeout(timer);
  }, [filters.title]);

  const queryFilters = {
    ...filters,
    title: search,
  };

  const {
    data,
    isPending,
    isError,
    error,
    refetch,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useAgentTickets(queryFilters);

  const tickets = data?.pages.flatMap((page) => page.tickets) ?? [];

  const total = data?.pages[0]?.total ?? 0;

  return (
    <div className="w-full space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          Agent Dashboard
        </h1>

        <p className="text-sm text-muted">
          Review and manage employee support tickets.
        </p>
      </header>

      <AgentTicketFilters filters={filters} onChange={setFilters} />

      <section aria-label="All support tickets" className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-foreground">All Tickets</h2>

          {!isPending && !isError && (
            <p className="text-sm text-muted">
              {total} matching {total === 1 ? "ticket" : "tickets"}
            </p>
          )}
        </div>

        {isPending && (
          <div
            role="status"
            className="rounded-xl border border-border bg-surface p-8 text-center text-sm text-muted"
          >
            Loading tickets...
          </div>
        )}

        {isError && (
          <div className="space-y-4">
            <Alert tone="danger" title="Unable to load tickets">
              {error.message}
            </Alert>

            <Button variant="secondary" onClick={() => void refetch()}>
              Try again
            </Button>
          </div>
        )}

        {!isPending && !isError && tickets.length === 0 && (
          <div className="rounded-xl border border-dashed border-border-strong bg-surface px-6 py-14 text-center">
            <h3 className="text-base font-semibold text-foreground">
              No tickets found
            </h3>

            <p className="mt-2 text-sm text-muted">
              Try changing your search or filters.
            </p>
          </div>
        )}

        {!isPending && !isError && tickets.length > 0 && (
          <>
            <Table>
              <THead>
                <Tr>
                  <Th scope="col">Title</Th>
                  <Th scope="col">Status</Th>
                  <Th scope="col">Category</Th>
                  <Th scope="col">Priority</Th>
                  <Th scope="col">Created on</Th>
                </Tr>
              </THead>

              <TBody>
                {tickets.map((ticket) => {
                  const category =
                    ticket.category !== "NOT_SPECIFIED"
                      ? ticket.category
                      : ticket.ai_category;

                  const priority =
                    ticket.priority !== "NOT_SPECIFIED"
                      ? ticket.priority
                      : ticket.ai_priority;

                  const aiCategory =
                    ticket.category === "NOT_SPECIFIED" &&
                    category !== "NOT_SPECIFIED";

                  const aiPriority =
                    ticket.priority === "NOT_SPECIFIED" &&
                    priority !== "NOT_SPECIFIED";

                  return (
                    <Tr key={ticket.id}>
                      <Td className="min-w-64 max-w-96">
                        <div className="space-y-1">
                          <Link
                            to={`/agent/tickets/${ticket.id}`}
                            className="font-medium text-foreground hover:text-brand hover:underline"
                          >
                            {ticket.title}
                          </Link>
                          <p className="truncate text-xs text-subtle">
                            {ticket.description}
                          </p>
                        </div>
                      </Td>

                      <Td>
                        <Badge
                          tone={
                            ticket.status === "RESOLVED" ? "resolved" : "open"
                          }
                        >
                          {formatLabel(ticket.status)}
                        </Badge>
                      </Td>

                      <Td>
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge tone={categoryTones[category]}>
                            {formatLabel(category)}
                          </Badge>

                          {aiCategory && (
                            <Badge tone="brand">AI specified</Badge>
                          )}
                        </div>
                      </Td>

                      <Td>
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge tone={priorityTones[priority]}>
                            {formatLabel(priority)}
                          </Badge>

                          {aiPriority && (
                            <Badge tone="brand">AI specified</Badge>
                          )}
                        </div>
                      </Td>

                      <Td className="whitespace-nowrap text-muted">
                        {formatDate(ticket.created_at)}
                      </Td>
                    </Tr>
                  );
                })}
              </TBody>
            </Table>

            <div className="flex flex-wrap items-center justify-between gap-4">
              <p className="text-sm text-muted">
                Showing {tickets.length} of {total} tickets
              </p>

              {hasNextPage && (
                <Button
                  type="button"
                  variant="secondary"
                  loading={isFetchingNextPage}
                  onClick={() => void fetchNextPage()}
                >
                  {isFetchingNextPage ? "Loading..." : "Load more"}
                </Button>
              )}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
