import { apiClient } from "../../../lib/apiClient";
import type {
  Ticket,
  TicketCategory,
  TicketPriority,
} from "../../employe/types";

export type TicketLogType =
  | "CATEGORY_CHANGE"
  | "PRIORITY_CHANGE"
  | "RESOLUTION_DESCRIPTION_CHANGE";

export type TicketAuditLog = {
  id: string;
  ticket_id: string;
  agent_id: string;
  log_type: TicketLogType;
  old_value: string | null;
  new_value: string | null;
  created_at: string;
};

export type UpdateTicketData = {
  category: TicketCategory;
  priority: TicketPriority;
};

export function getAgentTicket(ticketId: string) {
  return apiClient<Ticket>(`/tickets/${encodeURIComponent(ticketId)}`);
}

export function getTicketAuditLogs(ticketId: string) {
  return apiClient<TicketAuditLog[]>(
    `/users/logs/${encodeURIComponent(ticketId)}`,
  );
}

export function updateAgentTicket(ticketId: string, data: UpdateTicketData) {
  return apiClient<Ticket>(
    `/tickets/agent/update/${encodeURIComponent(ticketId)}`,
    {
      method: "PUT",
      body: data,
    },
  );
}
