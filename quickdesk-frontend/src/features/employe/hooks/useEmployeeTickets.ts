import { useInfiniteQuery } from "@tanstack/react-query";
import { getEmployeeTickets } from "../api/ticketAPI";

export function useEmployeeTickets() {
  return useInfiniteQuery({
    queryKey: ["employee", "tickets"],
    queryFn: ({ pageParam }) => getEmployeeTickets(pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? lastPage.page + 1 : undefined,
  });
}
