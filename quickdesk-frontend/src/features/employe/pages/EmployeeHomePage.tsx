import { useState } from "react";

import { Button } from "../../../components/ui/Button";
import { Alert } from "../../../components/ui/Alert";

import TicketCard from "../components/TicketCard";
import CreateTicketModal from "../components/CreateTicketModal";

import { useEmployeeTickets } from "../hooks/useEmployeeTickets";

export default function EmployeeHomePage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const {
    data,
    isPending,
    isError,
    error,
    refetch,
    isRefetching,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useEmployeeTickets();

  const tickets = data?.pages.flatMap((page) => page.tickets) ?? [];

  const total = data?.pages[0]?.total ?? 0;

  return (
    <div className="w-full space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            My Tickets
          </h1>

          <p className="text-sm text-muted">
            View and track your support requests.
          </p>
        </div>

        <Button
          type="button"
          variant="primary"
          size="md"
          onClick={() => setIsCreateModalOpen(true)}
        >
          + Create Ticket
        </Button>
      </header>

      <section aria-label="My support tickets" className="space-y-5">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-foreground">
            Your requests
          </h2>

          {!isPending && !isError && (
            <p className="text-sm text-muted">
              {total} {total === 1 ? "ticket" : "tickets"}
            </p>
          )}
        </div>

        {isPending && (
          <div
            role="status"
            aria-live="polite"
            className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3"
          >
            {Array.from({ length: 6 }).map((_, index) => (
              <div
                key={index}
                aria-hidden="true"
                className="h-64 animate-pulse rounded-xl border border-border bg-surface-muted"
              />
            ))}

            <span className="sr-only">Loading your tickets...</span>
          </div>
        )}

        {isError && (
          <div className="space-y-4">
            <Alert tone="danger" title="Unable to load tickets">
              {error.message}
            </Alert>

            <Button
              type="button"
              variant="secondary"
              onClick={() => void refetch()}
            >
              Try again
            </Button>
          </div>
        )}

        {!isPending && !isError && tickets.length === 0 && (
          <div className="rounded-xl border border-dashed border-border-strong bg-surface px-6 py-16 text-center">
            <div className="mx-auto max-w-md space-y-3">
              <h3 className="text-lg font-semibold text-foreground">
                No tickets yet
              </h3>

              <p className="text-sm leading-6 text-muted">
                You haven't created any support tickets yet. When you submit a
                request, you'll be able to track its status here.
              </p>
            </div>
          </div>
        )}

        {tickets.length > 0 && (
          <>
            {isRefetching && !isFetchingNextPage && (
              <p role="status" className="text-xs text-subtle">
                Refreshing tickets...
              </p>
            )}

            <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
              {tickets.map((ticket) => (
                <TicketCard key={ticket.id} ticket={ticket} />
              ))}
            </div>

            {hasNextPage && (
              <div className="flex justify-center pt-4">
                <Button
                  type="button"
                  variant="secondary"
                  loading={isFetchingNextPage}
                  disabled={isRefetching}
                  onClick={() => void fetchNextPage()}
                >
                  {isFetchingNextPage ? "Loading more..." : "Load more tickets"}
                </Button>
              </div>
            )}
          </>
        )}
      </section>

      {isCreateModalOpen && (
        <CreateTicketModal onClose={() => setIsCreateModalOpen(false)} />
      )}
    </div>
  );
}
