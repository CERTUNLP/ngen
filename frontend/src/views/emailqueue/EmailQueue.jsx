import React, { useEffect, useState } from "react";
import { Badge, Button, ButtonGroup, Card, Col, Form, Modal, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getEmailMessages, sendQueuedEmail, resendEmail, sendAllPending, getEmailQueueStats, discardEmail, retryEmail } from "api/services/emailqueue";
import { patchSetting } from "api/services/setting";
import { COMPONENT_URL } from "config/constant";
import TableEmailQueue from "./TableEmailQueue";
import DetailModalEmailQueue from "./DetailModalEmailQueue";
import AdvancedPagination from "components/Pagination/AdvancedPagination";
import Alert from "components/Alert/Alert";

const getStatusTabs = (t) => [
  { key: "all", label: t("ngen.email_queue.tab_all"), filter: "", statKey: "total" },
  { key: "pending", label: t("ngen.email_queue.pending"), filter: "sent=false&send_attempt_failed=false", statKey: "pending" },
  { key: "sent", label: t("ngen.email_queue.sent"), filter: "sent=true&send_attempt_failed=false", statKey: "sent_total" },
  { key: "failed", label: t("ngen.email_queue.failed"), filter: "send_attempt_failed=true", statKey: "failed" },
];

const EmailQueue = () => {
  const { t } = useTranslation();
  const STATUS_TABS = getStatusTabs(t);
  const [activeTab, setActiveTab] = useState("pending");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sendingId, setSendingId] = useState(null);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [confirmModal, setConfirmModal] = useState({ show: false, message: null, type: null });
  const [sendAllConfirm, setSendAllConfirm] = useState(false);
  const [toggleConfirm, setToggleConfirm] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [stats, setStats] = useState({});
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [order, setOrder] = useState("-created");
  const [refresh, setRefresh] = useState(false);

  const tab = STATUS_TABS.find((ti) => ti.key === activeTab) || STATUS_TABS[0];

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  const refreshAll = () => setRefresh((prev) => !prev);

  useEffect(() => {
    getEmailQueueStats()
      .then(setStats)
      .catch(() => {});
  }, [refresh]);

  useEffect(() => {
    setLoading(true);
    getEmailMessages(currentPage, tab.filter, order)
      .then((response) => {
        setMessages(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) setUpdatePagination(true);
        setDisabledPagination(false);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [currentPage, activeTab, order, refresh]);

  const handleSendNow = (msg) => {
    setConfirmModal({ show: true, message: msg, type: "send" });
  };

  const handleResend = (msg) => {
    setConfirmModal({ show: true, message: msg, type: "resend" });
  };

  const handleDiscard = async (msg) => {
    setSendingId(msg.id);
    try {
      await discardEmail(msg.id);
      refreshAll();
    } catch {
      // errors handled by service
    } finally {
      setSendingId(null);
    }
  };

  const handleRetry = async (msg) => {
    setSendingId(msg.id);
    try {
      await retryEmail(msg.id);
      refreshAll();
    } catch {
      // errors handled by service
    } finally {
      setSendingId(null);
    }
  };

  const handleConfirm = async () => {
    const { message, type } = confirmModal;
    setConfirmModal({ show: false, message: null, type: null });
    if (!message) return;

    setSendingId(message.id);
    try {
      if (type === "send") {
        await sendQueuedEmail(message.id);
      } else {
        await resendEmail(message.id);
      }
      refreshAll();
    } catch {
      // errors handled by service
    } finally {
      setSendingId(null);
    }
  };

  const handleToggleAutoSend = () => {
    setToggleConfirm(true);
  };

  const handleConfirmToggle = async () => {
    setToggleConfirm(false);
    const newValue = !stats.auto_send;
    setStats((prev) => ({ ...prev, auto_send: newValue }));
    try {
      await patchSetting(
        `${COMPONENT_URL.constance}EMAIL_AUTO_SEND/`,
        "EMAIL_AUTO_SEND",
        newValue
      );
    } catch {
      setStats((prev) => ({ ...prev, auto_send: !newValue }));
    }
  };

  const handleSendAllPending = async () => {
    setSendAllConfirm(false);
    try {
      await sendAllPending();
      refreshAll();
    } catch {
      // errors handled by service
    }
  };

  const handleShowDetail = (message) => {
    setSelectedMessage(message);
    setShowDetail(true);
  };

  const handleCloseDetail = () => {
    setShowDetail(false);
    setSelectedMessage(null);
  };

  return (
    <React.Fragment>
      <Alert component="emailmessage" />
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row className="align-items-center">
                <Col sm="auto">
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={refreshAll}
                    aria-label={t("ngen.retest.refresh")}
                    className="me-2"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      className="bi bi-arrow-clockwise"
                      viewBox="0 0 16 16"
                      aria-hidden="true"
                      focusable="false"
                    >
                      <path fillRule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z" />
                      <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
                    </svg>
                  </Button>
                </Col>
                <Col sm="auto">
                  <ButtonGroup size="sm" className="me-2">
                    {STATUS_TABS.map((ti) => (
                      <Button
                        key={ti.key}
                        variant={activeTab === ti.key ? "primary" : "outline-primary"}
                        onClick={() => {
                          setActiveTab(ti.key);
                          setCurrentPage(1);
                        }}
                      >
                        {ti.label}
                        {stats[ti.statKey] !== undefined && (
                          <Badge bg="light" text="dark" className="ms-1">
                            {stats[ti.statKey]}
                          </Badge>
                        )}
                      </Button>
                    ))}
                  </ButtonGroup>
                </Col>
                <Col sm="auto" className="d-flex align-items-center">
                  <Form.Check
                    type="switch"
                    id="auto-send-toggle"
                    checked={!!stats.auto_send}
                    onChange={handleToggleAutoSend}
                    label={
                      <small className="text-nowrap">
                        {stats.auto_send
                          ? t("ngen.email_queue.auto_send")
                          : t("ngen.email_queue.manual_send")}
                      </small>
                    }
                  />
                </Col>
                <Col sm="auto">
                  <Button
                    size="sm"
                    variant={!stats.pending || stats.pending === 0 ? "outline-secondary" : "outline-primary"}
                    onClick={() => setSendAllConfirm(true)}
                    disabled={!stats.pending || stats.pending === 0}
                    className="text-capitalize"
                  >
                    {t("ngen.email_queue.send_all")}
                  </Button>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <TableEmailQueue
                messages={messages}
                loading={loading}
                sendingId={sendingId}
                order={order}
                setOrder={setOrder}
                onSendNow={handleSendNow}
                onResend={handleResend}
                onRetry={handleRetry}
                onDiscard={handleDiscard}
                onShowDetail={handleShowDetail}
              />
            </Card.Body>
            <Card.Footer>
              <Row className="justify-content-md-center">
                <Col md="auto">
                  <AdvancedPagination
                    countItems={countItems}
                    updatePage={updatePage}
                    updatePagination={updatePagination}
                    setUpdatePagination={setUpdatePagination}
                    setLoading={setLoading}
                    disabledPagination={disabledPagination}
                    setDisabledPagination={setDisabledPagination}
                  />
                </Col>
              </Row>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
      {showDetail && selectedMessage && (
        <DetailModalEmailQueue message={selectedMessage} onClose={handleCloseDetail} />
      )}
      <Modal show={sendAllConfirm} onHide={() => setSendAllConfirm(false)} centered size="sm">
        <Modal.Header closeButton>
          <Modal.Title>{t("ngen.email_queue.send_all")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {t("ngen.email_queue.confirm_send_all", { count: stats.pending || 0 })}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-primary" onClick={handleSendAllPending}>
            {t("ngen.accept")}
          </Button>
          <Button variant="outline-secondary" onClick={() => setSendAllConfirm(false)}>
            {t("button.cancel")}
          </Button>
        </Modal.Footer>
      </Modal>
      <Modal show={toggleConfirm} onHide={() => setToggleConfirm(false)} centered size="sm">
        <Modal.Header closeButton>
          <Modal.Title>{t("ngen.email_queue.auto_send")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {stats.auto_send
            ? t("ngen.email_queue.confirm_auto_send_off")
            : t("ngen.email_queue.confirm_auto_send_on")}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-primary" onClick={handleConfirmToggle}>
            {t("ngen.accept")}
          </Button>
          <Button variant="outline-secondary" onClick={() => setToggleConfirm(false)}>
            {t("button.cancel")}
          </Button>
        </Modal.Footer>
      </Modal>
      <Modal show={confirmModal.show} onHide={() => setConfirmModal({ show: false, message: null, type: null })} centered size="sm">
        <Modal.Header closeButton>
          <Modal.Title>
            {confirmModal.type === "send" ? t("ngen.email_queue.send_now") : t("ngen.email_queue.resend")}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {confirmModal.type === "send"
            ? t("ngen.email_queue.confirm_send")
            : t("ngen.email_queue.confirm_resend")}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-primary" onClick={handleConfirm}>
            {t("ngen.accept")}
          </Button>
          <Button variant="outline-secondary" onClick={() => setConfirmModal({ show: false, message: null, type: null })}>
            {t("button.cancel")}
          </Button>
        </Modal.Footer>
      </Modal>
    </React.Fragment>
  );
};

export default EmailQueue;
