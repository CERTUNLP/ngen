import React from 'react';
import { Modal } from 'react-bootstrap';
import FormCase from './components/FormCase';
import { useTranslation, Trans } from 'react-i18next';


const ModalCreateCase = ({ showModalCase, setShowModalCase, caseItem, states, setCaseToLink, stateNames, setSelectCase, completeField1, selectedEvent, setSelectedEvent, refresh, setRefresh }) => {
  const { t } = useTranslation();
  return (
    <Modal show={showModalCase} size="lg" onHide={() => setShowModalCase(false)} aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Header closeButton>
        <Modal.Title>{t('ngen.add_eventcase')}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div id="example-collapse-text">
          <FormCase
            caseItem={caseItem}
            allStates={states}
            edit={false}
            save='Crear'
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
          />
        </div>
      </Modal.Body>
    </Modal>
  );
};

export default ModalCreateCase;
