import React, { useRef, useEffect, useState } from "react";
import { Modal, Button, Badge } from "react-bootstrap";
import { useTranslation } from "react-i18next";

const bodyStatus = (message, t) => {
  if (message.send_attempt_failed) return { label: t("ngen.email_queue.failed"), bg: "danger" };
  if (message.sent) return { label: t("ngen.email_queue.sent"), bg: "success" };
  return { label: t("ngen.email_queue.pending"), bg: "info" };
};

const DetailModalEmailQueue = ({ message, onClose }) => {
  const { t } = useTranslation();
  const iframeRef = useRef(null);
  const [iframeHeight, setIframeHeight] = useState(400);

  const htmlContent = message.body_html || message.body || "-";

  useEffect(() => {
    if (!iframeRef.current) return;
    const checkHeight = () => {
      try {
        const doc = iframeRef.current.contentDocument || iframeRef.current.contentWindow.document;
        if (doc && doc.body) {
          setIframeHeight(Math.max(400, doc.body.scrollHeight + 20));
        }
      } catch {
        // cross-origin, ignore
      }
    };
    iframeRef.current.addEventListener("load", checkHeight);
    return () => {
      if (iframeRef.current) {
        iframeRef.current.removeEventListener("load", checkHeight);
      }
    };
  }, [htmlContent]);

  const renderRecipients = (list) => {
    if (!list || list.length === 0) return "-";
    return list.map((r) => `${r.name || ""} <${r.email}>`).join(", ");
  };

  const renderAttachments = (list) => {
    if (!list || list.length === 0) return "-";
    return list.map((a) => a.name).join(", ");
  };

  const status = bodyStatus(message, t);

  return (
    <Modal show={true} onHide={onClose} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>
          {t("ngen.email_queue.detail_title", { id: message.id })}
          <Badge bg={status.bg} className="ms-2">{status.label}</Badge>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.subject")}</dt>
          <dd className="col-sm-9">{message.subject || "-"}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.from")}</dt>
          <dd className="col-sm-9">{message.senders?.map((s) => s.email).join(", ") || "-"}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.to")}</dt>
          <dd className="col-sm-9">{renderRecipients(message.recipients)}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.bcc")}</dt>
          <dd className="col-sm-9">{renderRecipients(message.bcc_recipients)}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.template")}</dt>
          <dd className="col-sm-9">{message.template || "-"}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.attachments")}</dt>
          <dd className="col-sm-9">{renderAttachments(message.attachments)}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.created")}</dt>
          <dd className="col-sm-9">{message.created || "-"}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.sent_date")}</dt>
          <dd className="col-sm-9">{message.date || "-"}</dd>
        </dl>
        <dl className="row mb-1">
          <dt className="col-sm-3">{t("ngen.email_queue.message_id")}</dt>
          <dd className="col-sm-9 text-break">{message.message_id || "-"}</dd>
        </dl>
        <hr />
        <h6>{t("ngen.email_queue.body_html")}</h6>
        <iframe
          ref={iframeRef}
          srcDoc={htmlContent}
          title={t("ngen.email_queue.body_html")}
          sandbox="allow-same-origin"
          style={{ width: "100%", height: iframeHeight, border: "1px solid #dee2e6", borderRadius: 4 }}
        />
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          {t("w.close")}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DetailModalEmailQueue;
