import React, { useEffect, useState } from "react";
import { Alert, Button, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { patchCaseState } from "api/services/cases";
import { getState } from "api/services/states";
import setAlert from "utils/setAlert";
import { currentUserHasPermissions } from "utils/permissions";

/**
 * Icon button that transitions a case to its "solved" child state, after
 * confirmation. Used both in the case list (TableCase) and the case detail
 * page (ReadCase).
 */
const CloseCaseButton = ({ caseItem, onClosed, solved }) => {
  const { t } = useTranslation();

  if (!currentUserHasPermissions(undefined, ["change_case", "change_case_network_admin"])) {
    return null;
  }

  const [showModal, setShowModal] = useState(false);
  const [closeInfo, setCloseInfo] = useState(null);
  const [closing, setClosing] = useState(false);
  const [detectedSolved, setDetectedSolved] = useState(false);

  useEffect(() => {
    if (solved === undefined && caseItem?.state) {
      getState(caseItem.state)
        .then((response) => setDetectedSolved(!!response.data.solved))
        .catch(() => {});
    }
  }, [caseItem?.state, solved]);

  const isSolved = solved !== undefined ? solved : detectedSolved;

  const handleClick = async () => {
    setClosing(true);
    try {
      const stateResponse = await getState(caseItem.state);
      const stateData = stateResponse.data;

      if (stateData.solved) {
        setAlert(t("ngen.case.close.already_closed"), "error", "case");
        return;
      }

      let targetStateUrl = null;
      for (const childUrl of stateData.children || []) {
        const childResponse = await getState(childUrl);
        if (childResponse.data.solved) {
          targetStateUrl = childResponse.data.url;
          break;
        }
      }

      if (!targetStateUrl) {
        setAlert(t("ngen.case.close.no_transition"), "error", "case");
        return;
      }

      setCloseInfo({
        eventCount: caseItem.events?.length ?? caseItem.events_count ?? 0,
        targetStateUrl
      });
      setShowModal(true);
    } catch (error) {
      console.error(error);
    } finally {
      setClosing(false);
    }
  };

  const handleConfirm = () => {
    if (!closeInfo || closing) return;
    setClosing(true);
    patchCaseState(caseItem.url, closeInfo.targetStateUrl)
      .then((response) => {
        onClosed?.(response);
        setShowModal(false);
        setCloseInfo(null);
      })
      .catch((error) => {
        console.error(error);
        const msg = error.response?.data?.detail
          || error.response?.data?.state?.[0]
          || t("ngen.case.close.error");
        setAlert(msg, "error", "case");
      })
      .finally(() => {
        setClosing(false);
      });
  };

  return (
    <React.Fragment>
      <Button
        type="button"
        className="btn-icon btn-rounded"
        variant="outline-success"
        title={t("ngen.case.close")}
        aria-label={t("ngen.case.close")}
        disabled={closing || isSolved}
        onClick={handleClick}
      >
        <i className="fas fa-lock" />
      </Button>
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>{t("ngen.case.close")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {closeInfo?.eventCount > 1 && (
            <Alert variant="warning">
              {t("ngen.case.close.warning", { count: closeInfo.eventCount })}
            </Alert>
          )}
          <p>{t("ngen.case.close.confirm")}</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={() => setShowModal(false)} disabled={closing}>
            {t("ngen.cancel")}
          </Button>
          <Button variant="outline-danger" onClick={handleConfirm} disabled={closing}>
            {t("ngen.case.close")}
          </Button>
        </Modal.Footer>
      </Modal>
    </React.Fragment>
  );
};

export default CloseCaseButton;
