import { useInfiniteQuery } from "@tanstack/react-query";

import { getAgentTickets } from "../api/agentApi";

import type { AgentTicketFilters } from "../api/agentApi";

export function useAgentTickets(filters: AgentTicketFilters) {
  return useInfiniteQuery({
    queryKey: [
      "agent",
      "tickets",
      filters.status,
      filters.category,
      filters.priority,
      filters.title,
    ],
    queryFn: ({ pageParam }) => getAgentTickets(filters, pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? lastPage.page + 1 : undefined,
  });
}
