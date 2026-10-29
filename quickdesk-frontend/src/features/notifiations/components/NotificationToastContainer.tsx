import type { NotificationToast } from "../types";

type Props = {
  toasts: NotificationToast[];
  onDismiss: (id: string) => void;
};

export default function NotificationToastContainer({
  toasts,
  onDismiss,
}: Props) {
  if (toasts.length === 0) return null;

  return (
    <div
      aria-label="Live notifications"
      className="
        pointer-events-none fixed bottom-4 right-4
        z-50 flex w-[calc(100%-2rem)]
        max-w-sm flex-col gap-3
        sm:bottom-6 sm:right-6
      "
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="status"
          aria-live="polite"
          className="
            pointer-events-auto
            rounded-xl border border-border
            bg-surface p-4 text-foreground
            shadow-lg
          "
        >
          <div className="flex items-start gap-3">
            <div
              className={
                toast.event === "TICKET_RESOLVED"
                  ? "flex size-9 shrink-0 items-center justify-center rounded-full bg-success-subtle text-success"
                  : "flex size-9 shrink-0 items-center justify-center rounded-full bg-brand-subtle text-brand"
              }
              aria-hidden="true"
            >
              {toast.event === "TICKET_RESOLVED" ? "✓" : "+"}
            </div>

            <div className="min-w-0 flex-1 space-y-1">
              <h3 className="text-sm font-semibold text-foreground">
                {toast.title}
              </h3>

              <p className="text-sm leading-5 text-muted">{toast.message}</p>
            </div>

            <button
              type="button"
              aria-label={`Dismiss ${toast.title} notification`}
              onClick={() => onDismiss(toast.id)}
              className="
                shrink-0 rounded-md px-2 py-1
                text-sm text-muted
                transition-colors
                hover:bg-surface-muted
                hover:text-foreground
                focus-visible:outline-2
                focus-visible:outline-brand
              "
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
