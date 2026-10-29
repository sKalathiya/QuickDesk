import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useNavigate } from "react-router";
import { logoutUser } from "../api/authApi";

export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: logoutUser,

    onSuccess: () => {
      queryClient.clear();

      navigate("/login", {
        replace: true,
      });
    },
  });
}
