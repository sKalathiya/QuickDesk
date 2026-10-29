import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema } from "../types";
import type { RegisterFormData } from "../types";
import { TextField } from "../../../components/ui/TextField";
import { Button } from "../../../components/ui/Button";
import { Link } from "react-router";

export default function RegisterForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });
  const onSubmit = (data: RegisterFormData) => {
    console.log(data);
    reset();
  };
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <TextField
        id="name"
        label="Name"
        hint="Enter your name"
        error={errors.name?.message}
        {...register("name")}
      />
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
      <TextField
        id="confirmPassword"
        label="Confirm Password"
        hint="Enter your confirm password"
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />
      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Registering..." : "Register"}
      </Button>
      <p className="text-sm text-muted">
        Already have an account?{" "}
        <Link
          to="/login"
          className="text-brand hover:underline font-medium ml-1"
        >
          Login
        </Link>
      </p>
    </form>
  );
}
