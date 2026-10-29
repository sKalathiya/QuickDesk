import { useQuery } from "@tanstack/react-query";

import { getAgentMetrics } from "../api/metricsApi";

export function useAgentMetrics() {
  return useQuery({
    queryKey: ["agent", "metrics"],
    queryFn: getAgentMetrics,
    staleTime: 30_000,
    retry: 1,
  });
}
