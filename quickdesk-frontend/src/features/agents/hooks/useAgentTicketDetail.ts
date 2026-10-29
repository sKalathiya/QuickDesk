import { useQuery } from "@tanstack/react-query";
import {
  getAgentTicket,
  getTicketAuditLogs,
} from "../api/agentTicketDetailApi";

export function useAgentTicketDetail(ticketId: string) {
  return useQuery({
    queryKey: ["agent", "ticket", ticketId],
    queryFn: () => getAgentTicket(ticketId),
    enabled: Boolean(ticketId),
  });
}

export function useTicketAuditLogs(ticketId: string) {
  return useQuery({
    queryKey: ["agent", "ticket", ticketId, "logs"],
    queryFn: () => getTicketAuditLogs(ticketId),
    enabled: Boolean(ticketId),
  });
}
