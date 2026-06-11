import React, { useState } from "react";
import { Badge, Button, Modal, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import { useTranslation } from "react-i18next";
import { getEmailFailmsg } from "api/services/emailqueue";

const statusBadge = (message, t, onClickError) => {
  if (message.send_attempt_failed) {
    return (
      <Badge
        bg="danger"
        style={{ cursor: "pointer" }}
        onClick={() => onClickError && onClickError(message)}
        title={t("ngen.email_queue.click_for_error")}
      >
        {t("ngen.email_queue.failed")}
      </Badge>
    );
  }
  if (message.sent) {
    return <Badge bg="success">{t("ngen.email_queue.sent")}</Badge>;
  }
  return <Badge bg="info">{t("ngen.email_queue.pending")}</Badge>;
};

const retryColumn = (msg, t, onRetry, sendingId) => {
  if (!msg.send_attempt_failed) return <span className="text-muted">-</span>;
  if (msg.retried) {
    return (
      <span className="text-success" title={t("ngen.email_queue.already_retried")}>
        <i className="fas fa-check-circle" /> {t("ngen.email_queue.retried")}
      </span>
    );
  }
  return (
    <CrudButton
      type="check"
      name=""
      text={t("ngen.email_queue.retry")}
      onClick={() => onRetry(msg)}
      disabled={sendingId === msg.id}
    />
  );
};

const TableEmailQueue = ({
  messages,
  loading,
  sendingId,
  onSendNow,
  onResend,
  onRetry,
  onDiscard,
  onShowDetail,
}) => {
  const { t } = useTranslation();
  const [errorModal, setErrorModal] = useState(null);
  const [errorText, setErrorText] = useState("");
  const [errorLoading, setErrorLoading] = useState(false);

  const handleShowError = async (msg) => {
    setErrorModal(msg);
    setErrorLoading(true);
    setErrorText("");
    try {
      const data = await getEmailFailmsg(msg.id);
      setErrorText(data.last_error || t("ngen.email_queue.no_error_detail"));
    } catch {
      setErrorText(t("ngen.email_queue.no_error_detail"));
    } finally {
      setErrorLoading(false);
    }
  };

  const handleCloseError = () => {
    setErrorModal(null);
    setErrorText("");
  };

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
    <>
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
            <th>{t("ngen.email_queue.retry")}</th>
            <th>{t("ngen.options")}</th>
          </tr>
        </thead>
        <tbody>
          {messages.length === 0 ? (
            <tr>
              <td colSpan={9} className="text-muted py-4">
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
                <td>{statusBadge(msg, t, handleShowError)}</td>
                <td>{retryColumn(msg, t, onRetry, sendingId)}</td>
                <td className="text-nowrap">
                  <CrudButton type="read" name="" text={t("w.view")} onClick={() => onShowDetail(msg)} />
                  {!msg.send_attempt_failed && (
                    <>
                      {!msg.sent && (
                        <>
                          <CrudButton
                            type="check"
                            name=""
                            text={t("ngen.email_queue.send_now")}
                            onClick={() => onSendNow(msg)}
                            disabled={sendingId === msg.id}
                          />
                          <CrudButton
                            type="delete"
                            name=""
                            text={t("ngen.email_queue.discard")}
                            onClick={() => onDiscard(msg)}
                            disabled={sendingId === msg.id}
                          />
                        </>
                      )}
                      {msg.sent && (
                        <CrudButton
                          type="create"
                          name=""
                          text={t("ngen.email_queue.resend")}
                          onClick={() => onResend(msg)}
                          disabled={sendingId === msg.id}
                        />
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>

      <Modal show={!!errorModal} onHide={handleCloseError} size="lg" centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {t("ngen.email_queue.error_title", { id: errorModal?.id })}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {errorLoading ? (
            <Row className="justify-content-md-center">
              <Spinner animation="border" variant="primary" />
            </Row>
          ) : (
            <pre className="text-danger bg-secondary bg-opacity-10 p-3 rounded" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", fontSize: "0.85rem", maxHeight: 400, overflow: "auto" }}>
              {errorText}
            </pre>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseError}>
            {t("w.close")}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default TableEmailQueue;
