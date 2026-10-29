import { Alert } from "../../../components/ui/Alert";
import { Button } from "../../../components/ui/Button";

import { useCurrentUser } from "../hooks/useCurrentUser";
import { useLogout } from "../hooks/useLogout";

export default function UserProfile() {
  const { data: user, isPending, isError, error, refetch } = useCurrentUser();

  const logoutMutation = useLogout();

  return (
    <div className="flex min-w-0 flex-wrap items-center justify-end gap-3">
      {isPending && (
        <span role="status" className="text-sm text-muted">
          Loading profile...
        </span>
      )}

      {user && (
        <div className="min-w-0 text-right">
          <p className="truncate text-sm font-semibold text-foreground">
            {user.name}
          </p>

          <p
            className="max-w-60 truncate text-xs text-muted"
            title={user.email}
          >
            {user.email}
          </p>
        </div>
      )}

      {isError && (
        <div className="space-y-2">
          <p className="text-xs text-danger">{error.message}</p>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => void refetch()}
          >
            Retry profile
          </Button>
        </div>
      )}

      <Button
        type="button"
        variant="secondary"
        size="md"
        loading={logoutMutation.isPending}
        onClick={() => logoutMutation.mutate()}
      >
        {logoutMutation.isPending ? "Logging out..." : "Logout"}
      </Button>

      {logoutMutation.isError && (
        <div className="w-full">
          <Alert tone="danger" title="Unable to log out">
            {logoutMutation.error.message}
          </Alert>
        </div>
      )}
    </div>
  );
}
