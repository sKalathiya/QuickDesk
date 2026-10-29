import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router";

import { loginSchema } from "../types";
import type { LoginFormData } from "../types";
import { useLogin } from "../hooks/useLogin";

import { TextField } from "../../../components/ui/TextField";
import { Button } from "../../../components/ui/Button";
import { Alert } from "../../../components/ui/Alert";

export default function LoginForm() {
  const navigate = useNavigate();
  const loginMutation = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await loginMutation.mutateAsync(data);

      // Temporary until current-user/role retrieval exists.
      navigate("/employee", { replace: true });
    } catch {
      // TanStack Query exposes the error through mutation.error.
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
      {loginMutation.isError && (
        <Alert tone="danger" title="Login failed">
          {loginMutation.error.message}
        </Alert>
      )}

      <TextField
        id="email"
        type="email"
        label="Email"
        placeholder="you@company.com"
        autoComplete="email"
        error={errors.email?.message}
        disabled={loginMutation.isPending}
        {...register("email")}
      />

      <TextField
        id="password"
        type="password"
        label="Password"
        placeholder="Enter your password"
        autoComplete="current-password"
        error={errors.password?.message}
        disabled={loginMutation.isPending}
        {...register("password")}
      />

      <Button
        type="submit"
        loading={loginMutation.isPending}
        className="w-full"
      >
        {loginMutation.isPending ? "Logging in..." : "Login"}
      </Button>

      <p className="text-sm text-muted">
        Don&apos;t have an account?{" "}
        <Link
          to="/register"
          className="ml-1 font-medium text-brand hover:underline"
        >
          Register
        </Link>
      </p>
    </form>
  );
}
