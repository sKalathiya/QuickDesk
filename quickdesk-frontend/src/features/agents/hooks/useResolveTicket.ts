import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  generateAIDraft,
  resolveAgentTicket,
} from "../api/agentTicketDetailApi";

export const aiDraftQueryKey = (ticketId: string) =>
  ["agent", "ticket", ticketId, "ai-draft"] as const;

export function useGenerateAIDraft(ticketId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => generateAIDraft(ticketId),

    retry: false,

    onSuccess: (draft) => {
      queryClient.setQueryData(aiDraftQueryKey(ticketId), draft);

      void queryClient.invalidateQueries({
        queryKey: ["agent", "ticket", ticketId],
      });
    },
  });
}

export function useResolveTicket(ticketId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (resolutionDescription: string) =>
      resolveAgentTicket(ticketId, resolutionDescription),

    retry: false,

    onSuccess: async (updatedTicket) => {
      queryClient.setQueryData(["agent", "ticket", ticketId], updatedTicket);

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["agent", "tickets"],
        }),
        queryClient.invalidateQueries({
          queryKey: ["agent", "ticket", ticketId, "logs"],
        }),
        queryClient.invalidateQueries({
          queryKey: ["agent", "metrics"],
        }),
      ]);
    },
  });
}
