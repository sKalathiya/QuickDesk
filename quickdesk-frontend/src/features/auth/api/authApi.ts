import { apiClient } from "../../../lib/apiClient";
import type {
  AuthUser,
  LoginFormData,
  LoginResponse,
  RegisterFormData,
} from "../types";

export async function registerUser(data: RegisterFormData): Promise<AuthUser> {
  const { name, email, password } = data;

  return apiClient<AuthUser>("/auth/register", {
    method: "POST",
    body: { name, email, password },
  });
}

export async function loginUser(data: LoginFormData): Promise<LoginResponse> {
  return apiClient<LoginResponse>("/auth/login", {
    method: "POST",
    body: {
      email: data.email,
      password: data.password,
    },
  });
}

export async function getCurrentUser(): Promise<AuthUser> {
  return apiClient<AuthUser>("/users/current-user", {
    method: "GET",
  });
}

export async function logoutUser(): Promise<void> {
  await apiClient<void>("/auth/logout", {
    method: "POST",
  });
}
