import { useMutation } from "@tanstack/react-query";
import { loginUser } from "../api/authApi";

export function useLogin() {
  return useMutation({
    mutationFn: loginUser,
  });
}
