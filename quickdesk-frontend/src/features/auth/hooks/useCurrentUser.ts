import { useQuery } from "@tanstack/react-query";
import { getCurrentUser } from "../api/authApi";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["auth", "current-user"],
    queryFn: getCurrentUser,
    retry: false,
    staleTime: 60_000,
  });
}
