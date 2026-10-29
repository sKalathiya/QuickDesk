import { useEffect, useRef, useState } from "react";
import type { MouseEvent } from "react";

import { useQueryClient } from "@tanstack/react-query";
import { Button } from "../../../components/ui/Button";
import { Alert } from "../../../components/ui/Alert";
import { TextArea } from "../../../components/ui/TextField";

import type { Ticket } from "../../employe/types";
import type { AIDraftResponse } from "../api/agentTicketDetailApi";

import {
  aiDraftQueryKey,
  useGenerateAIDraft,
  useResolveTicket,
} from "../hooks/useResolveTicket";

type Props = {
  ticket: Ticket;
  onClose: () => void;
};

export default function ResolveTicketModal({ ticket, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const generatingRef = useRef(false);

  const queryClient = useQueryClient();

  const draftMutation = useGenerateAIDraft(ticket.id);
  const resolveMutation = useResolveTicket(ticket.id);

  const cachedDraft = queryClient.getQueryData<AIDraftResponse>(
    aiDraftQueryKey(ticket.id),
  );

  const originalDraft = ticket.ai_resolution_description ?? "";

  const [draftText, setDraftText] = useState(
    cachedDraft?.answer ?? originalDraft,
  );

  const [draftGenerated, setDraftGenerated] = useState(
    Boolean(cachedDraft || originalDraft),
  );

  const [draftSource, setDraftSource] = useState(cachedDraft?.source ?? "");

  const [finalResponse, setFinalResponse] = useState("");

  const [validationError, setValidationError] = useState<string | null>(null);

  const isBusy = draftMutation.isPending || resolveMutation.isPending;

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
    if (isBusy) return;

    dialogRef.current?.close();
    onClose();
  };

  const handleBackdropClick = (event: MouseEvent<HTMLDialogElement>) => {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  };

  const handleGenerateDraft = async () => {
    if (generatingRef.current || draftGenerated || isBusy) {
      return;
    }

    generatingRef.current = true;
    draftMutation.reset();

    try {
      const draft = await draftMutation.mutateAsync();

      setDraftText(draft.answer);
      setDraftSource(draft.source);
      setDraftGenerated(true);
    } catch {
      // Errors are shown through draftMutation.
      // A failed request may be retried.
    } finally {
      generatingRef.current = false;
    }
  };

  const handleUseDraft = () => {
    setFinalResponse(draftText);
    setValidationError(null);
  };

  const handleResolve = async () => {
    const response = finalResponse.trim();

    if (!response) {
      setValidationError(
        "Please provide a resolution before resolving the ticket.",
      );
      return;
    }

    if (response.length > 4000) {
      setValidationError("Resolution must be 4000 characters or fewer.");
      return;
    }

    setValidationError(null);
    resolveMutation.reset();

    try {
      await resolveMutation.mutateAsync(response);

      dialogRef.current?.close();
      onClose();
    } catch {
      // Display the API error inside the modal.
    }
  };

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="resolve-ticket-title"
      aria-describedby="resolve-ticket-description"
      onClick={handleBackdropClick}
      onCancel={(event) => {
        event.preventDefault();
        handleClose();
      }}
      className="
        fixed inset-0 m-auto
        max-h-[calc(100dvh-2rem)]
        w-[calc(100%-2rem)] max-w-5xl
        overflow-y-auto rounded-xl
        border border-border bg-surface
        p-0 text-foreground shadow-lg
        backdrop:bg-gray-950/60
      "
    >
      <header className="flex items-start justify-between gap-4 border-b border-border px-6 py-5">
        <div className="min-w-0 space-y-1">
          <h2
            id="resolve-ticket-title"
            className="text-lg font-semibold tracking-tight text-foreground"
          >
            Resolve Ticket
          </h2>

          <p id="resolve-ticket-description" className="text-sm text-muted">
            Review an AI draft or write your own resolution before resolving
            this ticket.
          </p>

          <p className="break-words text-xs text-subtle">{ticket.title}</p>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="sm"
          disabled={isBusy}
          onClick={handleClose}
        >
          Close
        </Button>
      </header>

      <div className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-2">
        {/* LEFT: AI DRAFT */}
        <section className="min-w-0 space-y-5 rounded-xl border border-border bg-surface-muted p-4">
          <div className="space-y-2">
            <h3 className="text-base font-semibold text-foreground">
              AI Draft Reply
            </h3>

            <p className="text-sm leading-6 text-muted">
              Generate a knowledge-base-grounded suggestion. You can edit the
              draft before using it.
            </p>
          </div>

          <Button
            type="button"
            variant="secondary"
            loading={draftMutation.isPending}
            disabled={draftGenerated || isBusy}
            onClick={() => void handleGenerateDraft()}
          >
            {draftMutation.isPending
              ? "Generating draft..."
              : draftGenerated
                ? "Draft already generated"
                : "Generate AI Draft"}
          </Button>

          {draftMutation.isError && (
            <Alert tone="danger" title="AI draft generation failed">
              {draftMutation.error.message}
            </Alert>
          )}

          {draftGenerated ? (
            <>
              <TextArea
                id="ai-draft-reply"
                label="Suggested reply"
                value={draftText}
                onChange={(event) => setDraftText(event.target.value)}
                rows={10}
                maxLength={4000}
                disabled={isBusy}
              />

              {draftSource.trim() && (
                <div className="space-y-2 rounded-lg border border-brand/25 bg-brand-subtle p-4">
                  <h4 className="text-sm font-semibold text-brand-muted">
                    Knowledge Base Citations
                  </h4>

                  <p className="whitespace-pre-wrap break-all text-sm leading-6 text-foreground">
                    {draftSource}
                  </p>
                </div>
              )}

              {!draftSource.trim() && (
                <p className="text-xs text-subtle">
                  No citation information is available for this draft.
                </p>
              )}

              <Button
                type="button"
                variant="secondary"
                disabled={!draftText.trim() || isBusy}
                onClick={handleUseDraft}
              >
                Use This Draft
              </Button>
            </>
          ) : (
            <div className="rounded-lg border border-dashed border-border-strong bg-surface p-6">
              <p className="text-sm text-muted">
                No AI draft generated yet. You can generate one or write your
                own response on the right.
              </p>
            </div>
          )}
        </section>

        {/* RIGHT: FINAL RESOLUTION */}
        <section className="min-w-0 space-y-5">
          <div className="space-y-2">
            <h3 className="text-base font-semibold text-foreground">
              Final Resolution
            </h3>

            <p className="text-sm leading-6 text-muted">
              Write your response independently, or use and edit the AI draft
              before submitting.
            </p>
          </div>

          <TextArea
            id="final-resolution"
            label="Resolution message"
            placeholder="Explain how the employee can resolve the issue..."
            value={finalResponse}
            onChange={(event) => {
              setFinalResponse(event.target.value);
              setValidationError(null);
            }}
            rows={12}
            maxLength={4000}
            disabled={isBusy}
            error={validationError ?? undefined}
          />

          <p className="text-right text-xs text-subtle">
            {finalResponse.length}/4000 characters
          </p>

          {resolveMutation.isError && (
            <Alert tone="danger" title="Unable to resolve ticket">
              {resolveMutation.error.message}
            </Alert>
          )}

          <div className="rounded-lg bg-surface-muted p-4">
            <p className="text-sm text-muted">
              Resolving this ticket saves the final response and updates its
              status to Resolved.
            </p>
          </div>
        </section>
      </div>

      <footer className="flex flex-wrap justify-end gap-3 border-t border-border px-6 py-5">
        <Button
          type="button"
          variant="secondary"
          disabled={isBusy}
          onClick={handleClose}
        >
          Cancel
        </Button>

        <Button
          type="button"
          variant="primary"
          loading={resolveMutation.isPending}
          disabled={isBusy || !finalResponse.trim()}
          onClick={() => void handleResolve()}
        >
          {resolveMutation.isPending ? "Resolving..." : "Resolve Ticket"}
        </Button>
      </footer>
    </dialog>
  );
}
