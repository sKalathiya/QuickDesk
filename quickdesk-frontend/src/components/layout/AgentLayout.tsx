import { NavLink, Outlet } from "react-router";

import { Button } from "../ui/Button";

export default function AgentLayout() {
  return (
    <main className="min-h-screen bg-canvas px-4 py-6 sm:px-6">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <header className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-surface p-4">
          <h1 className="text-2xl font-bold tracking-wide text-brand">
            QuickDesk
          </h1>

          <nav
            aria-label="Agent navigation"
            className="flex items-center gap-2"
          >
            <NavLink
              to="/agent"
              end
              className={({ isActive }) =>
                [
                  "rounded-md px-4 py-2 text-sm font-semibold transition-colors",
                  isActive
                    ? "bg-surface-muted text-foreground"
                    : "text-muted hover:bg-surface-muted hover:text-foreground",
                ].join(" ")
              }
            >
              Tickets
            </NavLink>

            <NavLink
              to="/agent/metrics"
              className={({ isActive }) =>
                [
                  "rounded-md px-4 py-2 text-sm font-semibold transition-colors",
                  isActive
                    ? "bg-surface-muted text-foreground"
                    : "text-muted hover:bg-surface-muted hover:text-foreground",
                ].join(" ")
              }
            >
              Metrics
            </NavLink>
          </nav>

          <Button type="button" variant="secondary" size="md">
            Logout
          </Button>
        </header>

        <div className="w-full rounded-xl border border-border bg-surface p-4 sm:p-6">
          <Outlet />
        </div>
      </div>
    </main>
  );
}
