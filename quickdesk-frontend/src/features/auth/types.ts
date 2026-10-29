import { z } from "zod";

export const loginSchema = z.object({
  email: z.email({ message: "Valid email is required" }),
  password: z.string().min(1, { message: "Password is required" }),
});

export type LoginFormData = z.infer<typeof loginSchema>;

const PASSWORD_REGEX =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$/;

export const registerSchema = z
  .object({
    name: z
      .string({ message: "Name is required" })
      .min(1, { message: "Name must be at least 1 character" })
      .max(50, { message: "Name must be less than 50 characters" }),
    email: z.email({ message: "Valid email is required" }),
    password: z
      .string({ message: "Password is required" })
      .min(8, { message: "Password must be at least 8 characters" })
      .max(18, { message: "Password must be less than 18 characters" })
      .regex(PASSWORD_REGEX, {
        message:
          "Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character",
      }),
    confirmPassword: z
      .string({ message: "Confirm password is required" })
      .min(8, { message: "Confirm password must be at least 8 characters" })
      .max(18, { message: "Confirm password must be less than 18 characters" })
      .regex(PASSWORD_REGEX, {
        message:
          "Confirm password must contain at least one lowercase letter, one uppercase letter, one number, and one special character",
      }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;
