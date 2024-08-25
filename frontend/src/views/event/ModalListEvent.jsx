import React, { useEffect, useState } from 'react'
import { Button, Col, Modal, Row } from 'react-bootstrap'
import Search from '../../components/Search/Search'
import FilterSelectUrl from '../../components/Filter/FilterSelectUrl'
import AdvancedPagination from '../../components/Pagination/AdvancedPagination'
import TableEvents from './components/TableEvents'
import { getEvents } from '../../api/services/events'
import './ModalListEvent.css'
import { useTranslation } from 'react-i18next'
import Alert from '../../components/Alert/Alert'

const ModalListEvent = (props) => {
  const [loading, setLoading] = useState(true)
  const [order, setOrder] = useState('-date')
  const [countItems, setCountItems] = useState(0)
  const [showAlert, setShowAlert] = useState(false)
  const [events, setEvents] = useState([])
  const [disabledPagination, setDisabledPagination] = useState(true)
  const [caseIsNull] = useState('&case__isnull=true')
  const [parentIsNull] = useState('&parent__isnull=true')
  const { t } = useTranslation()

  useEffect(() => {
    getEvents(props.currentPage,
      props.taxonomyFilter + props.tlpFilter + props.feedFilter +
      props.wordToSearch + caseIsNull + parentIsNull).then((response) => {
      setEvents(response.data.results)
      setCountItems(response.data.count)
      if (props.currentPage === 1) {
        props.setUpdatePagination(true)
      }
      setDisabledPagination(false)
    }).catch((error) => {
      setShowAlert(true)
      console.log(error)
    }).finally(() => {
      setLoading(false)
      setShowAlert(true)
    })
  }, [
    props.currentPage,
    props.taxonomyFilter,
    props.tlpFilter,
    props.feedFilter,
    props.wordToSearch,
    props.updateList])

  function updatePage (chosenPage) {
    props.setCurrentPage(chosenPage)
  }

  return (
    <Modal
      show={props.showModalListEvent}
      onHide={props.closeModal}
      aria-labelledby="contained-modal-title-vcenter"
      centered
      dialogClassName="modal-90w"
    >
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)}
             component="event"/>
      <Modal.Header closeButton>
        <Modal.Title>{
          t('ngen.event_link')}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Row>
          <Col sm={12} lg={12}>
            <Search type={t('ngen.event_one')}
                    setWordToSearch={props.setWordToSearch}
                    wordToSearch={props.wordToSearch}
                    setLoading={setLoading}/>
          </Col>
        </Row>
        <br/>
        <Row>
          <Col sm={4} lg={4}>
            <FilterSelectUrl options={props.tlpList} itemName={t('ngen.tlp')}
                             partOfTheUrl="tlp"
                             itemFilter={props.tlpFilter}
                             itemFilterSetter={props.setTlpFilter}
                             setLoading={setLoading}
                             setCurrentPage={props.setCurrentPage}
                             value={props.selectTlpFilter}
                             setValue={props.setSelectTlpFilter}/>
          </Col>
          <Col sm={4} lg={4}>
            <FilterSelectUrl options={props.taxonomies}
                             itemName={t('ngen.taxonomy_other')}
                             partOfTheUrl="taxonomy"
                             itemFilter={props.taxonomyFilter}
                             itemFilterSetter={props.setTaxonomyFilter}
                             setLoading={setLoading}
                             setCurrentPage={props.setCurrentPage}
                             value={props.selectTaxonomyFilter}
                             setValue={props.setSelectTaxonomyFilter}/>
          </Col>
          <Col sm={4} lg={4}>
            <FilterSelectUrl options={props.feeds}
                             itemName={t('ngen.feed_other')} partOfTheUrl="feed"
                             itemFilter={props.feedFilter}
                             itemFilterSetter={props.setFeedFilter}
                             setLoading={setLoading}
                             setCurrentPage={props.setCurrentPage}
                             value={props.selectFeedFilter}
                             setValue={props.setSelectFeedFilter}/>
          </Col>
        </Row>
        <div id="example-collapse-text">
          <TableEvents
            events={events} loading={loading}
            selectedEvent={props.selectedEvent}
            setSelectedEvent={props.setSelectedEvent} order={order}
            setOrder={setOrder} setLoading={setLoading}
            currentPage={props.currentPage} taxonomyNames={props.taxonomyNames}
            feedNames={props.feedNames}
            tlpNames={props.tlpNames} 
            formCaseCheckbok={true} 
            disableColumnDelete={true} disableTemplate={true}
            disableColumnEdit={true} detailModal={false}
            modalEventDetail={props.modalEventDetail} disableUuid={false}
            disableColumOption={props.disableColumOption}
            disableDateModified={true} disableDate={false}
          />
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Row className="justify-content-md-center">
          <Col>
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
        <Button variant="outline-primary" onClick={props.linkEventsToCase}>
          Link
        </Button>
        <Button variant="outline-secondary"
                onClick={props.closeModal}>Cancel</Button>
      </Modal.Footer>
    </Modal>
  )
}

export default ModalListEvent
