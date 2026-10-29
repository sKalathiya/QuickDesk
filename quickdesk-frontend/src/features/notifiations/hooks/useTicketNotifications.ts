import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import type {
  NotificationRole,
  NotificationToast,
  TicketNotificationEvent,
} from "../types";

const TOAST_DURATION = 6000;
const MAX_VISIBLE_TOASTS = 5;
const MAX_REMEMBERED_EVENTS = 100;

const eventDetails: Record<
  TicketNotificationEvent,
  Pick<NotificationToast, "title" | "message">
> = {
  TICKET_CREATED: {
    title: "New ticket created",
    message: "A new employee support ticket is available.",
  },
  TICKET_RESOLVED: {
    title: "Ticket resolved",
    message: "One of your support tickets has been resolved.",
  },
};

export function useTicketNotifications(role: NotificationRole) {
  const queryClient = useQueryClient();

  const [toasts, setToasts] = useState<NotificationToast[]>([]);

  const timersRef = useRef<Map<string, number>>(new Map());
  const receivedIdsRef = useRef<Set<string>>(new Set());

  const dismissToast = useCallback((id: string) => {
    const timer = timersRef.current.get(id);

    if (timer !== undefined) {
      window.clearTimeout(timer);
      timersRef.current.delete(id);
    }

    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  useEffect(() => {
    const url =
      role === "AGENT"
        ? "/api/v1/notifications/agent/stream"
        : "/api/v1/notifications/employee/stream";

    const source = new EventSource(url, {
      withCredentials: true,
    });

    function handleNotification(
      eventType: TicketNotificationEvent,
      event: MessageEvent,
    ) {
      const eventId = event.lastEventId;

      // Prevent duplicate toasts if an event is redelivered.
      if (eventId && receivedIdsRef.current.has(eventId)) {
        return;
      }

      if (eventId) {
        receivedIdsRef.current.add(eventId);

        if (receivedIdsRef.current.size > MAX_REMEMBERED_EVENTS) {
          const oldest = receivedIdsRef.current.values().next().value;

          if (oldest) {
            receivedIdsRef.current.delete(oldest);
          }
        }
      }

      if (eventType === "TICKET_CREATED" && role === "AGENT") {
        void queryClient.invalidateQueries({
          queryKey: ["agent", "tickets"],
        });

        void queryClient.invalidateQueries({
          queryKey: ["agent", "metrics"],
        });
      }

      if (eventType === "TICKET_RESOLVED" && role === "EMPLOYEE") {
        void queryClient.invalidateQueries({
          queryKey: ["employee", "tickets"],
        });
      }

      const id = eventId || `${eventType}-${crypto.randomUUID()}`;

      const details = eventDetails[eventType];

      setToasts((current) => {
        const next = [
          ...current,
          {
            id,
            event: eventType,
            ...details,
          },
        ];

        return next.slice(-MAX_VISIBLE_TOASTS);
      });

      const timeout = window.setTimeout(() => {
        timersRef.current.delete(id);

        setToasts((current) => current.filter((toast) => toast.id !== id));
      }, TOAST_DURATION);

      timersRef.current.set(id, timeout);
    }

    const onTicketCreated = (event: MessageEvent) => {
      handleNotification("TICKET_CREATED", event);
    };

    const onTicketResolved = (event: MessageEvent) => {
      handleNotification("TICKET_RESOLVED", event);
    };

    if (role === "AGENT") {
      source.addEventListener("TICKET_CREATED", onTicketCreated);
    } else {
      source.addEventListener("TICKET_RESOLVED", onTicketResolved);
    }

    return () => {
      source.removeEventListener("TICKET_CREATED", onTicketCreated);

      source.removeEventListener("TICKET_RESOLVED", onTicketResolved);

      source.close();

      for (const timeout of timersRef.current.values()) {
        window.clearTimeout(timeout);
      }

      timersRef.current.clear();
      receivedIdsRef.current.clear();
    };
  }, [role, queryClient]);

  return {
    toasts,
    dismissToast,
  };
}
