import { useMutation } from "@tanstack/react-query";
import { registerUser } from "../api/authApi";

export function useRegister() {
  return useMutation({
    mutationFn: registerUser,
  });
}
