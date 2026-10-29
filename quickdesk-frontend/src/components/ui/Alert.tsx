import type { ReactNode } from "react";
import { cx } from "../../lib/cx";

type Tone = "info" | "success" | "warning" | "danger";

const tones: Record<Tone, string> = {
  info: "border-info/25 bg-info-subtle text-info",
  success: "border-success/25 bg-success-subtle text-success",
  warning: "border-warning/25 bg-warning-subtle text-warning",
  danger: "border-danger/25 bg-danger-subtle text-danger",
};

export function Alert({
  tone = "info",
  title,
  children,
}: {
  tone?: Tone;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div
      role={tone === "danger" ? "alert" : "status"}
      className={cx("rounded-lg border px-4 py-3", tones[tone])}
    >
      <p className="text-sm font-medium">{title}</p>
      {children ? <p className="mt-1 text-sm leading-5">{children}</p> : null}
    </div>
  );
}
