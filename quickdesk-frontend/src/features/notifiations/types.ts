export type NotificationRole = "AGENT" | "EMPLOYEE";

export type TicketNotificationEvent = "TICKET_CREATED" | "TICKET_RESOLVED";

export type NotificationToast = {
  id: string;
  event: TicketNotificationEvent;
  title: string;
  message: string;
};
