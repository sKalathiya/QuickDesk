import { Link, Outlet, useLocation } from "react-router";
import { Button } from "../ui/Button";

export default function EmployeeLayout() {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;
  return (
    <main className="min-h-screen bg-canvas flex flex-col items-center justify-start p-6 space-y-8">
      <header className="flex items-center justify-between p-4 border border-border rounded-xl w-full max-w-7xl bg-surface">
        <h1 className="text-2xl font-bold tracking-wide text-brand ">
          QuickDesk
        </h1>
        <nav className="flex items-center gap-2">
          <Link
            to="/employee/tickets"
            className={
              isActive("/employee/tickets")
                ? "font-semibold text-foreground bg-surface-muted rounded-md px-4 py-2 text-md tracking-wide"
                : "text-foreground font-semibold hover:bg-surface-muted rounded-md px-4 py-2 text-md tracking-wide"
            }
          >
            Tickets
          </Link>
        </nav>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="md">
            Logout
          </Button>
        </div>
      </header>
      <div className="w-full max-w-7xl rounded-xl border border-border bg-surface flex flex-col items-center justify-start p-4">
        <Outlet />
      </div>
    </main>
  );
}
