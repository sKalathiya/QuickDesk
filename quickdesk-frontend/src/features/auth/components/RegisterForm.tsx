import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router";

import { registerSchema } from "../types";
import type { RegisterFormData } from "../types";
import { useRegister } from "../hooks/useRegister";

import { TextField } from "../../../components/ui/TextField";
import { Button } from "../../../components/ui/Button";
import { Alert } from "../../../components/ui/Alert";

export default function RegisterForm() {
  const navigate = useNavigate();
  const registerMutation = useRegister();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    registerMutation.reset();

    try {
      await registerMutation.mutateAsync(data);

      navigate("/login", {
        replace: true,
        state: {
          message: "Account created successfully. Please log in.",
        },
      });
    } catch {
      // API errors are exposed through registerMutation.error.
    }
  };

  const isLoading = isSubmitting || registerMutation.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
      {registerMutation.isError && (
        <Alert tone="danger" title="Registration failed">
          {registerMutation.error.message}
        </Alert>
      )}

      <TextField
        id="name"
        label="Name"
        placeholder="Your full name"
        autoComplete="name"
        error={errors.name?.message}
        disabled={isLoading}
        {...register("name")}
      />

      <TextField
        id="email"
        type="email"
        label="Email"
        placeholder="you@company.com"
        autoComplete="email"
        error={errors.email?.message}
        disabled={isLoading}
        {...register("email")}
      />

      <TextField
        id="password"
        type="password"
        label="Password"
        placeholder="Create a password"
        autoComplete="new-password"
        error={errors.password?.message}
        disabled={isLoading}
        {...register("password")}
      />

      <TextField
        id="confirmPassword"
        type="password"
        label="Confirm Password"
        placeholder="Confirm your password"
        autoComplete="new-password"
        error={errors.confirmPassword?.message}
        disabled={isLoading}
        {...register("confirmPassword")}
      />

      <Button type="submit" loading={isLoading} className="w-full">
        {isLoading ? "Registering..." : "Register"}
      </Button>

      <p className="text-sm text-muted">
        Already have an account?{" "}
        <Link
          to="/login"
          className="ml-1 font-medium text-brand hover:underline"
        >
          Login
        </Link>
      </p>
    </form>
  );
}
