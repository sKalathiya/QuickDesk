import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateAgentTicket } from "../api/agentTicketDetailApi";

import type { UpdateTicketData } from "../api/agentTicketDetailApi";

export function useUpdateAgentTicket(ticketId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateTicketData) => updateAgentTicket(ticketId, data),

    onSuccess: async (updatedTicket) => {
      queryClient.setQueryData(["agent", "ticket", ticketId], updatedTicket);

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["agent", "ticket", ticketId, "logs"],
        }),
        queryClient.invalidateQueries({
          queryKey: ["agent", "tickets"],
        }),
      ]);
    },
  });
}
