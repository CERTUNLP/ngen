import React, { useContext, useRef, useEffect, useState } from "react";
import { Modal, Button, Badge, Row, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getEmailBody, getEmailFailmsg } from "api/services/emailqueue";
import { ThemeContext } from "contexts/ThemeContext";

const bodyStatus = (message, t) => {
  if (message.status === "failed") return { label: t("ngen.email_queue.failed"), bg: "danger" };
  if (message.status === "sent") return { label: t("ngen.email_queue.sent"), bg: "success" };
  if (message.status === "cancelled") return { label: t("ngen.email_queue.cancelled"), bg: "secondary" };
  if (message.status === "sending" || message.status === "retrying") {
    return { label: t("ngen.email_queue.sending"), bg: "warning" };
  }
  return { label: t("ngen.email_queue.pending"), bg: "info" };
};

const DetailModalEmailQueue = ({ message, onClose }) => {
  const { t } = useTranslation();
  const { isDark } = useContext(ThemeContext);
  const iframeRef = useRef(null);
  const [iframeHeight, setIframeHeight] = useState(400);
  const [bodyHtml, setBodyHtml] = useState(null);
  const [bodyLoading, setBodyLoading] = useState(true);
  const [failmsg, setFailmsg] = useState(null);

  useEffect(() => {
    if (!message?.id) return;
    setBodyLoading(true);
    setBodyHtml(null);
    setFailmsg(null);
    Promise.all([
      getEmailBody(message.id),
      message.status === "failed" || message.status === "retrying"
        ? getEmailFailmsg(message.id)
        : Promise.resolve(null),
    ])
      .then(([bodyData, failData]) => {
        setBodyHtml(bodyData.body_html || bodyData.body);
        if (failData) setFailmsg(failData);
      })
      .catch(() => {
        setBodyHtml(t("ngen.email_queue.no_body_detail") || "-");
        if (message.status === "failed" || message.status === "retrying") setFailmsg({ last_error: null });
      })
      .finally(() => setBodyLoading(false));
  }, [message?.id]);

  const htmlContent = bodyHtml || "-";

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
        {(message.status === "failed" || message.status === "retrying") && failmsg && (
          <dl className="row mb-1">
            <dt className="col-sm-3 text-danger">{t("ngen.email_queue.last_error")}</dt>
            <dd className="col-sm-9">
              <pre className="text-danger bg-secondary bg-opacity-10 p-2 rounded mb-0" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", fontSize: "0.8rem", maxHeight: 200, overflow: "auto" }}>
                {failmsg.last_error || t("ngen.email_queue.no_error_detail")}
              </pre>
            </dd>
          </dl>
        )}
        {message.size != null && (
          <dl className="row mb-1">
            <dt className="col-sm-3">{t("ngen.email_queue.size")}</dt>
            <dd className="col-sm-9">
              {message.size > 1024
                ? `${(message.size / 1024).toFixed(1)} KB`
                : `${message.size} B`}
            </dd>
          </dl>
        )}
        <hr />
        <h6>{t("ngen.email_queue.body_html")}</h6>
        {bodyLoading ? (
          <Row className="justify-content-md-center py-4">
            <Spinner animation="border" variant="primary" />
          </Row>
        ) : (
          <iframe
            ref={iframeRef}
            srcDoc={htmlContent}
            title={t("ngen.email_queue.body_html")}
            sandbox="allow-same-origin"
            style={{ width: "100%", height: iframeHeight, border: "1px solid #dee2e6", borderRadius: 4 }}
          />
        )}
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
