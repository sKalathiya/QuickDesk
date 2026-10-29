import { z } from "zod";
export type TicketStatus = "OPEN" | "RESOLVED";

export type TicketCategory =
  | "IT"
  | "HR"
  | "FINANCE"
  | "ADMIN"
  | "OTHER"
  | "NOT_SPECIFIED";

export type TicketPriority = "LOW" | "MEDIUM" | "HIGH" | "NOT_SPECIFIED";

export type Ticket = {
  id: string;
  title: string;
  description: string;
  fileName: string | null;
  status: TicketStatus;
  category: TicketCategory;
  priority: TicketPriority;
  ai_category: TicketCategory;
  ai_priority: TicketPriority;
  resolutionDescription: string | null;
  ai_resolution_description: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
};

export type TicketListResponse = {
  tickets: Ticket[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
};

export const createTicketSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, "Ticket title is required")
    .max(255, "Title must be 255 characters or fewer"),

  description: z
    .string()
    .trim()
    .min(1, "Description is required")
    .max(4000, "Description must be 4000 characters or fewer"),

  fileName: z
    .string()
    .trim()
    .max(255, "Filename must be 255 characters or fewer"),
});

export type CreateTicketFormData = z.infer<typeof createTicketSchema>;
