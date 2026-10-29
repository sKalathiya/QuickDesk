import { apiClient } from "../../../lib/apiClient";
import type {
  TicketCategory,
  TicketPriority,
  TicketStatus,
  TicketListResponse,
} from "../../employe/types";

export type AgentTicketFilters = {
  status: TicketStatus | "";
  category: TicketCategory | "";
  priority: TicketPriority | "";
  title: string;
};

export async function getAgentTickets(
  filters: AgentTicketFilters,
  page: number,
): Promise<TicketListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: "20",
  });

  if (filters.status) params.set("status", filters.status);
  if (filters.category) params.set("category", filters.category);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.title.trim()) {
    params.set("title", filters.title.trim());
  }

  return apiClient<TicketListResponse>(`/tickets/?${params.toString()}`, {
    method: "GET",
  });
}
