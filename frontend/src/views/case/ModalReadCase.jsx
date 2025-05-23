import React from "react";
import { Button, Modal } from "react-bootstrap";
import ReadCase from "./ReadCase";
import { useTranslation } from "react-i18next";
import "./ModalReadCase.css";

const ModalReadCase = ({ modalShowCase, tableDetail, returnToListOfCases, linkCaseToEvent, closeModalDetail }) => {
  const { t } = useTranslation();

  return (
    <Modal
      show={modalShowCase}
      size="lg"
      onHide={tableDetail ? closeModalDetail : returnToListOfCases}
      aria-labelledby="contained-modal-title-vcenter"
      centered
      dialogClassName="modal-90w"
    >
      <Modal.Header closeButton />
      <Modal.Body>
        <div id="example-collapse-text">
          <ReadCase useLocalStorage={true} />
        </div>
      </Modal.Body>
      {tableDetail ? (
        ""
      ) : (
        <Modal.Footer>
          <Button variant="outline-primary" onClick={linkCaseToEvent}>
            &nbsp;
            {t("button.link")}
          </Button>
          <Button variant="outline-secondary" onClick={returnToListOfCases}>
            &nbsp;
            {t("button.return")}
          </Button>
        </Modal.Footer>
      )}
    </Modal>
  );
};

export default ModalReadCase;
