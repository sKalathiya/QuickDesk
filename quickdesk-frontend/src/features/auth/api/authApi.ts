import { apiClient } from "../../../lib/apiClient";
import type { AuthUser, LoginFormData, RegisterFormData } from "../types";

export async function registerUser(data: RegisterFormData): Promise<AuthUser> {
  const { name, email, password } = data;

  return apiClient<AuthUser>("/auth/register", {
    method: "POST",
    body: {
      name,
      email,
      password,
    },
  });
}

export async function loginUser(data: LoginFormData): Promise<void> {
  await apiClient<unknown>("/auth/login", {
    method: "POST",
    body: {
      email: data.email,
      password: data.password,
    },
  });
}

export async function logoutUser(): Promise<void> {
  await apiClient<null>("/auth/logout", {
    method: "POST",
  });
}
