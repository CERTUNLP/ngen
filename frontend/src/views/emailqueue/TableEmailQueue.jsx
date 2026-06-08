import React from "react";
import { Badge, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import { useTranslation } from "react-i18next";

const statusBadge = (message, t) => {
  if (message.send_attempt_failed) {
    return <Badge bg="danger">{t("ngen.email_queue.failed")}</Badge>;
  }
  if (message.sent) {
    return <Badge bg="success">{t("ngen.email_queue.sent")}</Badge>;
  }
  return <Badge bg="info">{t("ngen.email_queue.pending")}</Badge>;
};

const TableEmailQueue = ({
  messages,
  loading,
  sendingId,
  onSendNow,
  onResend,
  onShowDetail,
}) => {
  const { t } = useTranslation();

  const getRecipientSummary = (recipients) => {
    if (!recipients || recipients.length === 0) return "-";
    const emails = recipients.map((r) => r.email);
    if (emails.length <= 2) return emails.join(", ");
    return `${emails[0]}, ${emails[1]} +${emails.length - 2}`;
  };

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  return (
    <Table responsive hover className="text-center">
      <thead>
        <tr>
          <th>#</th>
            <th>{t("date.creation")}</th>
            <th>{t("ngen.email_queue.subject")}</th>
            <th>{t("ngen.email_queue.recipients")}</th>
            <th>{t("ngen.email_queue.template")}</th>
            <th>{t("ngen.email_queue.attachments")}</th>
          <th>{t("ngen.email_queue.status")}</th>
          <th>{t("ngen.options")}</th>
        </tr>
      </thead>
      <tbody>
        {messages.length === 0 ? (
          <tr>
            <td colSpan={8} className="text-muted py-4">
              {t("w.no_data")}
            </td>
          </tr>
        ) : (
          messages.map((msg) => (
            <tr key={msg.id}>
              <td>{msg.id}</td>
              <td className="text-nowrap">{msg.created?.slice(0, 16).replace("T", " ")}</td>
              <td className="text-start text-truncate" style={{ maxWidth: 220 }}>
                {msg.subject || "-"}
              </td>
              <td className="text-start text-truncate" style={{ maxWidth: 180 }} title={getRecipientSummary(msg.recipients)}>
                {getRecipientSummary(msg.recipients)}
              </td>
              <td className="text-nowrap">{msg.template || "-"}</td>
              <td>{msg.attachment_count ?? 0}</td>
              <td>{statusBadge(msg, t)}</td>
              <td className="text-nowrap">
                <CrudButton type="read" name="" text={t("w.view")} onClick={() => onShowDetail(msg)} />
                {!msg.sent && !msg.dispatched && (
                  <CrudButton
                    type="check"
                    name=""
                    text={t("ngen.email_queue.send_now")}
                    onClick={() => onSendNow(msg)}
                    disabled={sendingId === msg.id}
                  />
                )}
                <CrudButton
                  type="create"
                  name=""
                  text={t("ngen.email_queue.resend")}
                  onClick={() => onResend(msg)}
                  disabled={sendingId === msg.id}
                />
              </td>
            </tr>
          ))
        )}
      </tbody>
    </Table>
  );
};

export default TableEmailQueue;
