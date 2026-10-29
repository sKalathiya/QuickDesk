import { useEffect, useRef } from "react";
import type { MouseEvent } from "react";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "../../../components/ui/Button";
import { TextField, TextArea } from "../../../components/ui/TextField";
import { Alert } from "../../../components/ui/Alert";

import { createTicketSchema, type CreateTicketFormData } from "../types";
import { useCreateTicket } from "../hooks/useCreateTicket";

type CreateTicketModalProps = {
  onClose: () => void;
};

export default function CreateTicketModal({ onClose }: CreateTicketModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const createMutation = useCreateTicket();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateTicketFormData>({
    resolver: zodResolver(createTicketSchema),
    defaultValues: {
      title: "",
      description: "",
      fileName: "",
    },
  });

  const isLoading = isSubmitting || createMutation.isPending;

  useEffect(() => {
    const dialog = dialogRef.current;

    if (!dialog) return;

    if (!dialog.open) {
      dialog.showModal();
    }

    return () => {
      if (dialog.open) {
        dialog.close();
      }
    };
  }, []);

  const handleClose = () => {
    if (isLoading) return;

    dialogRef.current?.close();
    onClose();
  };

  const handleBackdropClick = (event: MouseEvent<HTMLDialogElement>) => {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  };

  const onSubmit = async (data: CreateTicketFormData) => {
    createMutation.reset();

    try {
      await createMutation.mutateAsync(data);
      dialogRef.current?.close();
      onClose();
    } catch {
      // API errors are displayed through the mutation.
    }
  };

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="create-ticket-title"
      aria-describedby="create-ticket-description"
      onClick={handleBackdropClick}
      onCancel={(event) => {
        event.preventDefault();
        handleClose();
      }}
      className="
        fixed inset-0 m-auto
        max-h-[calc(100dvh-2rem)]
        w-[calc(100%-2rem)] max-w-xl
        overflow-y-auto
        rounded-xl border border-border
        bg-surface p-0 text-foreground shadow-lg
        backdrop:bg-gray-950/60
      "
    >
      <div className="flex flex-col">
        <header className="flex items-start justify-between gap-4 border-b border-border px-6 py-5">
          <div className="space-y-1.5">
            <h2
              id="create-ticket-title"
              className="text-lg font-semibold tracking-tight text-foreground"
            >
              Create Ticket
            </h2>

            <p id="create-ticket-description" className="text-sm text-muted">
              Describe your issue so our support team can help you.
            </p>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            aria-label="Close create ticket dialog"
            disabled={isLoading}
            onClick={handleClose}
          >
            Close
          </Button>
        </header>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-6 px-6 py-6"
          noValidate
        >
          {createMutation.isError && (
            <Alert tone="danger" title="Unable to create ticket">
              {createMutation.error.message}
            </Alert>
          )}

          <TextField
            id="ticket-title"
            label="Ticket Title"
            placeholder="Briefly describe your issue"
            hint="Use a clear, specific title."
            maxLength={255}
            error={errors.title?.message}
            disabled={isLoading}
            {...register("title")}
          />

          <TextArea
            id="ticket-description"
            label="Description"
            placeholder="Explain what happened, what you expected, and any relevant details..."
            hint="Include enough details for the support team to understand the issue."
            rows={6}
            maxLength={4000}
            error={errors.description?.message}
            disabled={isLoading}
            {...register("description")}
          />

          <TextField
            id="ticket-filename"
            label="Filename (optional)"
            placeholder="example: screenshot.png"
            hint="Enter a filename if relevant. This field does not upload a file."
            maxLength={255}
            error={errors.fileName?.message}
            disabled={isLoading}
            {...register("fileName")}
          />

          <div className="flex flex-col-reverse gap-3 border-t border-border pt-5 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              disabled={isLoading}
              onClick={handleClose}
            >
              Cancel
            </Button>

            <Button type="submit" variant="primary" loading={isLoading}>
              {isLoading ? "Creating ticket..." : "Create Ticket"}
            </Button>
          </div>
        </form>
      </div>
    </dialog>
  );
}
