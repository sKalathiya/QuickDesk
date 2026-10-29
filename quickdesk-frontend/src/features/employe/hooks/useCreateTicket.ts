import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createTicket } from "../api/ticketAPI";

export function useCreateTicket() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTicket,
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["employee", "tickets"],
      });
    },
  });
}
