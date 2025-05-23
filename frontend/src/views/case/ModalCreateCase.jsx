import React from "react";
import { Modal } from "react-bootstrap";
import FormCase from "./components/FormCase";
import { useTranslation } from "react-i18next";

const ModalCreateCase = ({
  showModalCase,
  setShowModalCase,
  caseItem,
  states,
  setCaseToLink,
  stateNames,
  setSelectCase,
  completeField1,
  selectedEvent,
  setSelectedEvent,
  refresh,
  setRefresh,
  asNetworkAdmin
}) => {
  const { t } = useTranslation();
  return (
    <Modal show={showModalCase} size="lg" onHide={() => setShowModalCase(false)} aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Header closeButton>
        <Modal.Title>{t("ngen.case.create")}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div id="example-collapse-text">
          <FormCase
            caseItem={caseItem}
            allStates={states}
            edit={false}
            save={t("ngen.case.create")}
            evidenceColum={false}
            buttonsModalColum={false}
            createCaseModal={true}
            setShowModalCase={setShowModalCase}
            setCaseToLink={setCaseToLink}
            setSelectCase={setSelectCase}
            completeField1={completeField1}
            stateNames={stateNames}
            disableTableEvent={true}
            disableEvidence={true}
            disableTitle={true}
            selectedEvent={selectedEvent}
            setSelectedEvent={setSelectedEvent}
            refresh={refresh}
            setRefresh={setRefresh}
            asNetworkAdmin={asNetworkAdmin}
            disableTags={true}
          />
        </div>
      </Modal.Body>
    </Modal>
  );
};

export default ModalCreateCase;
