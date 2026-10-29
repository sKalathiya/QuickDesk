import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema } from "../types";
import type { LoginFormData } from "../types";
import { TextField } from "../../../components/ui/TextField";
import { Button } from "../../../components/ui/Button";
import { Link } from "react-router";

export default function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });
  const onSubmit = (data: LoginFormData) => {
    console.log(data);
    reset();
  };
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <TextField
        id="email"
        label="Email"
        hint="Enter your email address"
        error={errors.email?.message}
        {...register("email")}
      />

      <TextField
        id="password"
        label="Password"
        hint="Enter your password"
        error={errors.password?.message}
        {...register("password")}
      />
      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Logging in..." : "Login"}
      </Button>
      <p className="text-sm text-muted">
        Don&apos;t have an account?{" "}
        <Link
          to="/register"
          className="text-brand hover:underline font-medium ml-1"
        >
          Register
        </Link>
      </p>
    </form>
  );
}
