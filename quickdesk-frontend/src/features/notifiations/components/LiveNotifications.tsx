import type { NotificationRole } from "../types";

import { useTicketNotifications } from "../hooks/useTicketNotifications";
import NotificationToastContainer from "./NotificationToastContainer";

type Props = {
  role: NotificationRole;
};

export default function LiveNotifications({ role }: Props) {
  const { toasts, dismissToast } = useTicketNotifications(role);

  return (
    <NotificationToastContainer toasts={toasts} onDismiss={dismissToast} />
  );
}
