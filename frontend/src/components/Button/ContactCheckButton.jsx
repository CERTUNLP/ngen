import React, { useEffect, useState } from "react";
import { Button, Card, CloseButton, Col, Modal, Row, Table, ButtonGroup } from "react-bootstrap";
import {
  resendContactCheck,
  resendContactCheckByContactId,
  getContactCheckByContactId,
  getContactCheck,
  setContactCheckConfirmed
} from "api/services/contactchecks";
import DateShowField from "components/Field/DateShowField";
import CrudButton from "components/Button/CrudButton";
import { BsArrowRightShort, BsInfoCircle } from "react-icons/bs";
import { useTranslation } from "react-i18next";

const ContactCheckButton = ({ url, contact_url }) => {
  const { t } = useTranslation();
  const [urlToUse, setUrlToUse] = useState(url);
  const [sent, setSent] = useState(0);
  const [contactCheck, setContactCheck] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSetConfirmedModal, setShowSetConfirmedModal] = useState(false);

  useEffect(() => {
    if (urlToUse) {
      getContactCheck(urlToUse)
        .then((response) => {
          setContactCheck(response.data);
        })
        .catch((error) => {
          console.error(`${t("ngen.contactcheck.error")}:`, error);
        });
    } else if (contact_url) {
      const contactId = contact_url.split("/")[contact_url.split("/").length - 2];
      getContactCheckByContactId(contactId).then((response) => {
        setContactCheck(response.data && response.data.length > 0 ? response.data[0] : null);
      });
    }
  }, [urlToUse, sent]);

  const getBadgeText = () => {
    if (!contactCheck) return "";
    if (contactCheck.confirmed === true) return `${t("ngen.contactcheck.confirmed")}`;
    if (contactCheck.confirmed === false) return `${t("ngen.contactcheck.rejected")}`;
    if (contactCheck.is_pending === true) return `${t("ngen.contactcheck.pending")}`;
    return `${t("ngen.contactcheck.not_pending")}`;
  };

  const getBadgeColor = () => {
    if (!contactCheck) return "#999";
    if (contactCheck.confirmed === true) return "#28a745"; // green
    if (contactCheck.confirmed === false) return "#dc3545"; // red
    return "#ffc107"; // yellow
  };

  const handleBadgeClick = () => setShowPopup(true);
  const handleClosePopup = () => setShowPopup(false);
  const handleResendClick = (e) => {
    e.stopPropagation(); // evita abrir el popup del badge
    setShowConfirmModal(true);
  };

  const handleConfirmResend = () => {
    const resendPromise =
      contactCheck != null
        ? resendContactCheck(contactCheck.uuid)
        : resendContactCheckByContactId(contact_url.split("/")[contact_url.split("/").length - 2]);

    resendPromise
      .then((response) => {
        setShowConfirmModal(false);
        setSent(sent + 1);
        setContactCheck(null);
        setUrlToUse(response.data.url);
      })
      .catch((err) => {
        console.error(err);
      });
  };

  const showModalSetConfirmed = () => {
    setContactCheckConfirmed(contactCheck)
      .then((response) => {
        setUrlToUse(response.data.url);
        setSent(sent + 1);
        setShowPopup(false);
      })
      .catch((error) => {
        console.error(`${t("ngen.contactcheck.error")}:`, error);
        setShowPopup(false);
      });
    setShowPopup(false);
  };

  const handleSetConfirmed = (contactCheck) => {
    if (contactCheck) {
      showModalSetConfirmed(contactCheck);
      setShowPopup(false);
    }
  };

  const handleConfirmSetConfirmed = () => {
    if (contactCheck) {
      showModalSetConfirmed(contactCheck);
    }
    setShowSetConfirmedModal(false);
  };

  const handleCancelResend = () => setShowConfirmModal(false);

  const handleCancelSetConfirmed = () => setShowSetConfirmedModal(false);

  //   if (!contactCheck) return null;

  return (
    <>
      <ButtonGroup className="me-2" size="sm">
        {urlToUse && contactCheck && (
          <Button
            variant={getBadgeColor()}
            onClick={handleBadgeClick}
            title={t("w.show_details")}
            style={{
              fontWeight: "bold",
              paddingLeft: "0.75rem",
              paddingRight: "0.75rem",
              color: "#333",
              backgroundColor: getBadgeColor(),
              borderColor: "rgba(0,0,0,0.1)"
            }}
          >
            {getBadgeText()}
          </Button>
        )}
        <Button variant={"btn btn-outline-primary"} onClick={handleResendClick} title={t("ngen.contactcheck.resend")}>
          <BsArrowRightShort />
        </Button>
      </ButtonGroup>

      {showPopup && contactCheck && (
        <Modal size="lg" show={showPopup} onHide={() => setShowPopup(false)} aria-labelledby="contained-modal-title-vcenter" centered>
          <Modal.Body>
            <Row>
              <Col>
                <Card>
                  <Card.Header>
                    <Row>
                      <Col>
                        <Card.Title as="h5">{t("ngen.contactcheck.title")}</Card.Title>
                        <span className="d-block m-t-5">{t("ngen.contactcheck.detail")}</span>
                      </Col>
                      <Col sm={2} lg={2}>
                        <CloseButton aria-label={t("w.close")} onClick={() => setShowPopup(false)} />
                      </Col>
                    </Row>
                  </Card.Header>
                  <Card.Body>
                    <Table responsive>
                      <tbody>
                        <tr>
                          <td>{t("ngen.date.created")}</td>
                          <td>
                            <DateShowField value={contactCheck.created} />
                          </td>
                        </tr>
                        <tr>
                          <td>{t("ngen.date.modified")}</td>
                          <td>
                            <DateShowField value={contactCheck.modified} />
                          </td>
                        </tr>
                        <tr>
                          <td>{t("ngen.uuid")}</td>
                          <td>{contactCheck.uuid}</td>
                        </tr>
                        <tr>
                          <td>
                            {t("ngen.contactcheck.confirmed")}
                            <span style={{ marginLeft: 8, color: "#007bff" }}>
                              <BsInfoCircle title={t("ngen.contactcheck.confirmed_without_access_date")} />
                            </span>
                          </td>
                          <td>
                            {contactCheck.confirmed === null ? (
                              <>
                                <span>{t("ngen.unknown")}</span>{" "}
                                <CrudButton type="check" to={`#`} onClick={() => setShowSetConfirmedModal(true)} />
                              </>
                            ) : contactCheck.confirmed ? (
                              t("ngen.contactcheck.confirmed")
                            ) : (
                              t("ngen.contactcheck.rejected")
                            )}
                          </td>
                        </tr>
                        <tr>
                          <td>{t("ngen.date.accessed")}</td>
                          <td>
                            {contactCheck.accessed_at ? (
                              <DateShowField value={contactCheck.accessed_at} />
                            ) : (
                              t("ngen.contactcheck.no_access_date")
                            )}
                          </td>
                        </tr>
                        <tr>
                          <td>{t("ngen.contactcheck.pending")}</td>
                          <td>{contactCheck.is_pending ? t("ngen.yes") : t("ngen.no")}</td>
                        </tr>
                        <tr>
                          <td>{t("ngen.contactcheck.notes")}</td>
                          <td>
                            {(contactCheck.notes || t("ngen.contactcheck.no_notes")).split("\n").map((line, idx) => (
                              <span key={idx}>
                                {line}
                                <br />
                              </span>
                            ))}
                          </td>
                        </tr>
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Modal.Body>
        </Modal>
      )}

      {showConfirmModal && (
        <div
          style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "#fff",
            border: "1px solid #ccc",
            borderRadius: 8,
            padding: 24,
            zIndex: 10000,
            minWidth: 300,
            boxShadow: "0 2px 16px rgba(0,0,0,0.2)"
          }}
        >
          <h5>{t("ngen.contactcheck.resend_title")}</h5>
          <p>{t("ngen.contactcheck.resend_description")}</p>
          <div className="d-flex justify-content-end mt-3">
            <Button variant="secondary" onClick={handleCancelResend} className="me-2">
              {t("button.cancel")}
            </Button>
            <Button variant="primary" onClick={handleConfirmResend}>
              {t("button.send")}
            </Button>
          </div>
        </div>
      )}
      {showSetConfirmedModal && (
        <div
          style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "#fff",
            border: "1px solid #ccc",
            borderRadius: 8,
            padding: 24,
            zIndex: 10000,
            minWidth: 300,
            boxShadow: "0 2px 16px rgba(0,0,0,0.2)"
          }}
        >
          <h5>{t("ngen.contactcheck.set_confirmed_title")}</h5>
          <p>{t("ngen.contactcheck.set_confirmed_description")}</p>
          <div className="d-flex justify-content-end mt-3">
            <Button variant="secondary" onClick={handleCancelSetConfirmed} className="me-2">
              {t("button.cancel")}
            </Button>
            <Button variant="primary" onClick={handleConfirmSetConfirmed}>
              {t("button.send")}
            </Button>
          </div>
        </div>
      )}
    </>
  );
};

export default ContactCheckButton;
