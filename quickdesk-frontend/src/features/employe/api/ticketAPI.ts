import { apiClient } from "../../../lib/apiClient";
import type {
  CreateTicketFormData,
  Ticket,
  TicketListResponse,
} from "../types";

export async function getEmployeeTickets(
  page: number = 1,
): Promise<TicketListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: "12",
  });

  return apiClient<TicketListResponse>(`/tickets/?${params.toString()}`, {
    method: "GET",
  });
}

export async function createTicket(
  data: CreateTicketFormData,
): Promise<Ticket> {
  return apiClient<Ticket>("/tickets/", {
    method: "POST",
    body: {
      title: data.title,
      description: data.description,
      fileName: data.fileName || null,
    },
  });
}
