import { apiClient } from "../../../lib/apiClient";

import type {
  TicketCategory,
  TicketPriority,
  TicketStatus,
} from "../../employe/types";

export type AgentMetrics = {
  total_tickets: number;
  tickets_by_status: Record<TicketStatus, number>;
  tickets_by_category: Record<TicketCategory, number>;
  tickets_by_priority: Record<TicketPriority, number>;
  median_resolution_time: number;
  agent_overridden_tickets_percentage: number;
};

export function getAgentMetrics(): Promise<AgentMetrics> {
  return apiClient<AgentMetrics>("/users/dashboard", {
    method: "GET",
  });
}
