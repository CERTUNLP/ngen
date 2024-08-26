import React, { useEffect, useState } from 'react';
import { Button, Col, Modal, Row } from 'react-bootstrap';
import Search from '../../components/Search/Search';
import FilterSelectUrl from '../../components/Filter/FilterSelectUrl';
import TableCase from './components/TableCase';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import { getCases } from '../../api/services/cases';
import { useTranslation } from 'react-i18next';
import './ModalListCase.css';
import Alert from '../../components/Alert/Alert';

const ModalListCase = (props) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [order, setOrder] = useState('-date');

  const [cases, setCases] = useState([]);
  const [countItems, setCountItems] = useState(0);
  const [showAlert, setShowAlert] = useState(false);

  const [disabledPagination, setDisabledPagination] = useState(true);

  useEffect(() => {
    getCases(props.currentPage, props.stateFilter + props.tlpFilter + props.priorityFilter + props.wordToSearch, order)
      .then((response) => {
        setCases(response.data.results);
        setCountItems(response.data.count);
        if (props.currentPage === 1) {
          props.setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true); //este tiene que ser enviado por props
        setLoading(false);
      });
  }, [props.wordToSearch, props.priorityFilter, props.currentPage, props.tlpFilter, props.stateFilter, order]);

  function updatePage(chosenPage) {
    props.setCurrentPage(chosenPage);
  }

  return (
    <Modal
      size="lg"
      show={props.showModalListCase}
      onHide={props.closeModal}
      aria-labelledby="contained-modal-title-vcenter"
      dialogClassName="modal-90w"
      centered
    >
      <Modal.Header closeButton>
        <Modal.Title>{t('ngen.case_link')}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {showAlert && <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="case" />}
        <Row>
          <Col sm={12} lg={12}>
            <Search
              type={t('ngen.case_one')}
              setWordToSearch={props.setWordToSearch}
              wordToSearch={props.wordToSearch}
              setLoading={setLoading}
            />
          </Col>
        </Row>
        <br />
        <Row>
          <Col sm={4} lg={4}>
            <FilterSelectUrl
              options={props.priorities}
              itemName={t('ngen.priority_one')}
              partOfTheUrl="priority"
              itemFilter={props.priorityFilter}
              itemFilterSetter={props.setPriorityFilter}
              setLoading={setLoading}
              setCurrentPage={props.setCurrentPage}
            />
          </Col>
          <Col sm={4} lg={4}>
            <FilterSelectUrl
              options={props.tlp}
              itemName={t('ngen.tlp')}
              partOfTheUrl="tlp"
              itemFilter={props.tlpFilter}
              itemFilterSetter={props.setTlpFilter}
              setLoading={setLoading}
              setCurrentPage={props.setCurrentPage}
            />
          </Col>
          <Col sm={4} lg={4}>
            <FilterSelectUrl
              options={props.allStates}
              itemName={t('ngen.state_one')}
              partOfTheUrl="state"
              itemFilter={props.stateFilter}
              itemFilterSetter={props.setStateFilter}
              setLoading={setLoading}
              setCurrentPage={props.setCurrentPage}
            />
          </Col>
        </Row>
        <div id="example-collapse-text">
          <TableCase
            cases={cases}
            loading={loading}
            selectedCases={props.selectedCases}
            setSelectedCases={props.setSelectedCases}
            order={order}
            setOrder={setOrder}
            setLoading={setLoading}
            priorityNames={props.priorityNames}
            stateNames={props.stateNames}
            tlpNames={props.tlpNames}
            userNames={props.userNames}
            editColum={false}
            deleteColum={false}
            detailModal={true}
            modalCaseDetail={props.modalCaseDetail}
            navigationRow={false}
            selectCase={true}
            handleClickRadio={props.handleClickRadio}
            setSelectCase={props.setSelectCase}
            disableNubersOfEvents={true}
            disableDateModified={true}
          />
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Row className="justify-content-md-center">
          <Col md="auto">
            <AdvancedPagination
              countItems={countItems}
              updatePage={updatePage}
              updatePagination={props.updatePagination}
              setUpdatePagination={props.setUpdatePagination}
              setLoading={setLoading}
              setDisabledPagination={setDisabledPagination}
              disabledPagination={disabledPagination}
            />
          </Col>
        </Row>
      </Modal.Footer>
      <Modal.Footer>
        <Button variant="outline-primary" onClick={props.linkCaseToEvent}>
          {t('button.link')}
        </Button>
        <Button variant="outline-secondary" onClick={props.closeModal}>
          {t('button.cancel')}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ModalListCase;
