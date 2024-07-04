import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom'
import { Card, Row, Col, Button, Badge, Collapse, Form, Modal } from 'react-bootstrap';
import Navigation from '../../components/Navigation/Navigation'
import Search from '../../components/Search/Search'
import CrudButton from '../../components/Button/CrudButton';
import TableEvents from './components/TableEvents';
//filters
import FilterSelectUrl from '../../components/Filter/FilterSelectUrl';
import FilterSelect from '../../components/Filter/FilterSelect';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import ModalConfirm from '../../components/Modal/ModalConfirm';
import Alert from '../../components/Alert/Alert';
import ButtonFilter from '../../components/Button/ButtonFilter';
import { patchCase } from "../../api/services/cases";
//filters
import { getEvents, mergeEvent } from "../../api/services/events";
import { getMinifiedFeed } from "../../api/services/feeds";
import { getMinifiedTaxonomy } from '../../api/services/taxonomies';
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedState } from '../../api/services/states';
import ModalCreateCase from '../case/ModalCreateCase';
import ModalListCase from '../case/ModalListCase';
import { getMinifiedPriority } from '../../api/services/priorities';
import ModalReadCase from '../case/ModalReadCase';
import { getMinifiedUser } from '../../api/services/users';
import { useTranslation, Trans } from 'react-i18next';

const ListEvent = () => {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [refresh, setRefresh] = useState(true)
  //url by name
  // tlp feed
  const [taxonomyNames, setTaxonomyNames] = useState({});
  const [feedNames, setFeedNames] = useState({});
  const [tlpNames, setTlpNames] = useState({});

  //pagination
  const [countItems, setCountItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1)

  const [ifModify, setIfModify] = useState(null)
  const [showAlert, setShowAlert] = useState(false)
  //event merge Event
  //merge
  const [selectedEvent, setSelectedEvent] = useState([]);
  const [showModal, setShowModal] = useState(false);
  //filters and search
  const [wordToSearch, setWordToSearch] = useState('')
  const [taxonomyFilter, setTaxonomyFilter] = useState('')

  const [tlpFilter, setTlpFilter] = useState('')
  const [feedFilter, setFeedFilter] = useState('')

  const [tlpList, setTlpList] = useState([])
  const [taxonomies, setTaxonomies] = useState([]);
  const [feeds, setFeeds] = useState([])

  const [order, setOrder] = useState("-date");
  const [starDateFilter, setStarDateFilter] = useState("")
  const [endDateFilter, setEndDateFilter] = useState("")
  const [starDate, setStarDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [filterDate, setFilterDate] = useState(false)
  const [open, setOpen] = useState(false);
  const [updatePagination, setUpdatePagination] = useState(false)
  const [disabledPagination, setDisabledPagination] = useState(true)
  const types = [{ value: "true", label: "Eventos sin casos asignados" }, { value: "false", label: "Eventos con casos asignados" }]
  const [caseIsNull, setCaseIsNull] = useState('')
  //add to cases
  const [openCases, setOpenCases] = useState(true);

  //modal case
  const [showModalCase, setShowModalCase] = useState(false);

  const [showOptionsToAddCase, setShowOptionsToAddCase] = useState(false)
  const [showModalListCase, setShowModalListCase] = useState(false);

  const caseItem = {
    lifecycle: '',//required
    priority: '', //required
    tlp: '', //required
    state: '', //required
    date: null, //required
    name: "",
    parent: null,
    assigned: null,
    attend_date: null, //imprime la hora actual +3horas
    solve_date: null,
    comments: [], //?
    evidence: [],
  }
  const [stateNames, setStateNames] = useState({})
  const [states, setStates] = useState([]) //multiselect
  const [priorityNames, setPriorityNames] = useState({});
  const [allPriorities, setAllPriorities] = useState([])
  const [userNames, setUserNames] = useState({});
  const [selectedCases, setSelectedCases] = useState([]);
  const [caseToLink, setCaseToLink] = useState({});
  const [modalShowCase, setModalShowCase] = useState(false);

  //case variables
  const [currentPageCase, setCurrentPageCase] = useState(1)
  const [tlpFilterCase, setTlpFilterCase] = useState('')
  const [wordToSearchCase, setWordToSearchCase] = useState('')
  const [stateFilter, setStateFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [selectCase, setSelectCase] = useState("")//puede que se use en el multiselect, tengo ver bien cual es su utilidad
  const [updatePaginationCase, setUpdatePaginationCase] = useState(false)

  const { t } = useTranslation();

  useEffect(() => {
    getMinifiedUser().then((response) => { //se hardcodea las paginas
      let dicUser = {}
      response.map((user) => {
        dicUser[user.url] = user.username
      })
      setUserNames(dicUser)
    })
      .catch((error) => {
        console.log(error)

      })
    getMinifiedState().then((response) => {
      let list = []
      let dicState = {};
      response.map((stateItem) => {
        list.push({ value: stateItem.url, label: stateItem.name })
        dicState[stateItem.url] = stateItem.name;
      })
      setStates(list)
      setStateNames(dicState)
    })
      .catch((error) => {
        console.log(error)
      })
    getMinifiedTaxonomy().then((response) => {
      let listTaxonomies = [];
      let dicTaxonomy = {};
      response.map((taxonomy) => {
        listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name });
        dicTaxonomy[taxonomy.url] = taxonomy.name;
      });
      setTaxonomyNames(dicTaxonomy);
      setTaxonomies(listTaxonomies);
    });
    getMinifiedPriority().then((response) => {
      let listPriority = []
      let dicPriority = {}
      response.map((priority) => {
        listPriority.push({ value: priority.url, label: priority.name })
        dicPriority[priority.url] = priority.name
      })
      setPriorityNames(dicPriority)
      setAllPriorities(listPriority)
    })
      .catch((error) => {
        console.log(error)
      })

    getMinifiedFeed().then((response) => {
      let listFeeds = [];
      let dicFeed = {};
      response.map((feed) => {
        listFeeds.push({ value: feed.url, label: feed.name });
        dicFeed[feed.url] = feed.name;
      });
      setFeedNames(dicFeed);
      setFeeds(listFeeds);
    });

    getMinifiedTlp().then((response) => {
      let listTlp = [];
      let dicTlp = {};
      response.map((tlp) => {
        listTlp.push({ value: tlp.url, label: tlp.name });
        dicTlp[tlp.url] = { name: tlp.name, color: tlp.color };
      });
      setTlpList(listTlp);
      setTlpNames(dicTlp);
    });
  }, []);

  useEffect(() => {
    getEvents(currentPage, starDateFilter + endDateFilter + taxonomyFilter + tlpFilter + feedFilter + caseIsNull + wordToSearch, order)
      .then((response) => {
        setEvents(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setFilterDate(false);
        setDisabledPagination(false);
      })
      .catch((error) => {
        setShowAlert(true); // ¿Hace falta?
        console.log(error);
      })
      .finally(() => {
        setLoading(false);
        setShowAlert(true);
      });
  }, [currentPage, ifModify, wordToSearch, taxonomyFilter, tlpFilter, feedFilter, filterDate, order, caseIsNull, refresh]);

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  const reloadPage = () => {
    setRefresh(!refresh)
  }

  const mergeConfirm = () => {
    //setId
    setShowModal(true);
  }

  const merge = () => {
    const parent = selectedEvent.shift();
    selectedEvent.forEach(child => {
      console.log(`MERGE --> parent: ${parent} \n          child:${child} `)
      mergeEvent(parent, child)
        .then(response => setIfModify(response))
        .catch(error => console.log(error))
        .finally(() => {
          setSelectedEvent([])
          setShowModal(false)
        })
    });
  }

  const modalCase = () => {
    //setId
    //setUpdatePagination(true)
    setShowOptionsToAddCase(true)
  }

  const completeDateStar = (date) => {
    setStarDate(date)
    setStarDateFilter("created_range_after=" + date + '&')
    if ((endDateFilter !== "") && (starDateFilter !== "created_range_after=" + date + '&')) { // este if esta porque si no hay cambios en el WordToSearch 
      //haciendo que no se vuelva a ejecutar el useEffect y qeu al setearce setloading en true quede en un bucle infinito
      setFilterDate(true)
      setLoading(true)
    }
  }

  const completeDateEnd = (date) => {
    setEndDate(date)
    setEndDateFilter("created_range_before=" + date + '&')
    if ((endDateFilter !== "created_range_before=" + date + '&') && (starDateFilter !== "")) { // este if esta porque si no hay cambios en el WordToSearch 
      //haciendo que no se vuelva a ejecutar el useEffect y qeu al setearce setloading en true quede en un bucle infinito
      setFilterDate(true)
      setLoading(true)
    }
  }

  const clearModal = () => {
    setShowModalCase(false)
  };

  const closeOptionsList = () => {
    setShowOptionsToAddCase(false)
    setShowModalListCase(true)
    setUpdatePaginationCase(true)
  };

  const closeOptionsCreate = () => {
    setShowOptionsToAddCase(false)
    setShowModalCase(true)
  };

  function closeModal() {
    setShowModalListCase(false)
    //setUpdatePagination(true)
    setCurrentPageCase(1);
    setTlpFilterCase("")
    setPriorityFilter("")
    setStateFilter("")
    setWordToSearchCase("")
  }

  const handleClickRadio = (event, url, name, date, priority, tlp, state, user) => {
    const selectedId = event.target.id;
    if (selectedCases) {
      // Si es radio button, solo debe haber uno seleccionado
      setSelectedCases([selectedId]);
    } else {
      // Si es checkbox, permitir selección múltiple
      setSelectedCases(prevSelected =>
        prevSelected.includes(selectedId)
          ? prevSelected.filter(id => id !== selectedId)
          : [...prevSelected, selectedId]
      );
    }
    setCaseToLink({ value: url, name: name, date: date, priority: priority, tlp: tlp, state: state, user: user })
  };

  const modalCaseDetail = (url, name, date, priority, tlp, state, user) => {
    localStorage.setItem('case', url);
    setModalShowCase(true)
    setShowModalListCase(false)
    localStorage.setItem('navigation', false);
    localStorage.setItem('button return', false);
    setCaseToLink({ value: url, name: name, date: date, priority: priority, tlp: tlp, state: state, user: user })
  }

  const returnToListOfCases = () => {
    setShowModalListCase(true)
    setModalShowCase(false)
    setUpdatePaginationCase(true)
  };
  const linkCaseToEvent = () => {
    patchCase(caseToLink.value, selectedEvent).then((response) => {
      setSelectedEvent([])
      setSelectedCases("")
      setIfModify(response)
      setShowModalListCase(false)
      setModalShowCase(false)
      setCurrentPageCase(1);
      setTlpFilterCase("")
      setPriorityFilter("")
      setStateFilter("")
      setWordToSearchCase("")
      setUpdatePaginationCase(true)

    })

  };
  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="event" />
      <Row>
        <Navigation actualPosition={t('ngen.event_other')} />
      </Row>
      <Card>
        <Card.Header>
          <Row>
            <Col sm={1} lg={1}>
              <ButtonFilter open={open} setOpen={setOpen} />
            </Col>
            <Col sm={8} lg={4} >
              <Search type={t('search.taxonomy_feed_affectedresource')} setWordToSearch={setWordToSearch} wordToSearch={wordToSearch} setLoading={setLoading} />
            </Col>
            <Col>
              <Link to={"/events/create"} >
                <CrudButton type='create' name={t('ngen.event_one')} />
              </Link>
              <Button
                disabled={selectedEvent.length > 1 ? false : true}
                size="lm"
                className='text-capitalize'
                variant="outline-dark"
                title='Mergear'
                onClick={() => mergeConfirm()}>
                <i className="fa fa-code-branch" />
                {t('Merge')}&nbsp;
                <Badge
                  className="badge mr-1" >
                  {selectedEvent.length}
                </Badge>
              </Button>
              <Button
                disabled={selectedEvent.length > 0 ? false : true}
                size="lm"
                variant="outline-dark"
                onClick={() => modalCase()}>
                {t('ngen.case.addto')}
                <Badge
                  className="badge mr-1" >
                  {selectedEvent.length}
                </Badge>
              </Button>
              <Button
                size="lm"
                variant="outline-dark"
                onClick={() => reloadPage()}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-arrow-clockwise" viewBox="0 0 16 16">
                  <path fillRule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z" />
                  <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
                </svg>
              </Button>
            </Col>
          </Row>
          <Collapse in={open}>
            <div id="example-collapse-text">
              <Row>
                <Col sm={12} lg={6}>
                  <Form.Group controlId="formGridAddress1">
                    <Form.Label>{t('date.condition_from')}</Form.Label>
                    <Form.Control
                      type="date"
                      maxLength="150"
                      placeholder={t('date.condition_from')}
                      value={starDate}
                      onChange={(e) => completeDateStar(e.target.value)}
                      name="date" />
                  </Form.Group>
                </Col>
                <Col sm={12} lg={6}>
                  <Form.Group controlId="formGridAddress1">
                    <Form.Label>{t('date.condition_to')}</Form.Label>
                    <Form.Control
                      type="date"
                      maxLength="150"
                      value={endDate}
                      onChange={(e) => completeDateEnd(e.target.value)}
                      name="date" />
                  </Form.Group>
                </Col>
              </Row>
              <Row>
                <Col sm={4} lg={4}>
                  <FilterSelectUrl options={tlpList} itemName="tlp" partOfTheUrl="tlp" itemFilter={tlpFilter} itemFilterSetter={setTlpFilter} setLoading={setLoading} setCurrentPage={setCurrentPage} />
                </Col>
                <Col sm={4} lg={4}>
                  <FilterSelectUrl options={taxonomies} itemName={t('ngen.taxonomy_one')} partOfTheUrl="taxonomy" itemFilter={taxonomyFilter} itemFilterSetter={setTaxonomyFilter} setLoading={setLoading} setCurrentPage={setCurrentPage} />
                </Col>
                <Col sm={4} lg={4}>
                  <FilterSelectUrl options={feeds} itemName={t('ngen.feed_other')} partOfTheUrl="feed" itemFilter={feedFilter} itemFilterSetter={setFeedFilter} setLoading={setLoading} setCurrentPage={setCurrentPage} />
                </Col>
              </Row>
              <Row>
                <Col sm={4} lg={4}>
                  <FilterSelect options={types} partOfTheUrl="case__isnull" setFilter={setCaseIsNull} currentFilter={caseIsNull} setLoading={setLoading} placeholder={t('ngen.filter_case')} />
                </Col>
              </Row>
              <br />
            </div>
          </Collapse>
        </Card.Header>
        <Card.Body>
          <TableEvents events={events} loading={loading} selectedEvent={selectedEvent} setSelectedEvent={setSelectedEvent} order={order} setOrder={setOrder}
            setLoading={setLoading} currentPage={currentPage} taxonomyNames={taxonomyNames} feedNames={feedNames} tlpNames={tlpNames} disableCheckbox={false} disableUuid={false} />
        </Card.Body>
        <Card.Footer >
          <Row className="justify-content-md-center">
            <Col md="auto">
              <AdvancedPagination countItems={countItems} updatePage={updatePage} updatePagination={updatePagination} setUpdatePagination={setUpdatePagination} setLoading={setLoading} setDisabledPagination={setDisabledPagination} disabledPagination={disabledPagination} />
            </Col>
          </Row>
        </Card.Footer>

        <ModalConfirm type='merge' component={t('ngen.event_other')} name={selectedEvent} showModal={showModal} onHide={() => setShowModal(false)} ifConfirm={() => merge()} />

        <Modal show={showOptionsToAddCase} size="lg" onHide={() => setShowOptionsToAddCase(false)} aria-labelledby="contained-modal-title-vcenter" centered>
          <Modal.Header closeButton>
            <Modal.Title>{t('ngen.add.eventcase')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Button variant="primary" className='text-capitalize' size="sm" onClick={() => closeOptionsList()} aria-expanded={openCases}>
              {t('button.case_existing')}
            </Button>
            <Button variant="primary" className='text-capitalize' size="sm" onClick={() => closeOptionsCreate()} aria-expanded={openCases}>
              {t('button.case_new')}
            </Button>
          </Modal.Body>
        </Modal>
        <ModalCreateCase showModalCase={showModalCase} setShowModalCase={setShowModalCase} caseItem={caseItem}
          states={states} setSelectCase={setSelectCase} stateNames={states}
          evidenceColum={false} buttonsModalColum={false} createCaseModal={true} selectedEvent={selectedEvent}
          setSelectedEvent={setSelectedEvent} refresh={refresh} setRefresh={setRefresh} />

        <ModalListCase stateNames={stateNames} showModalListCase={showModalListCase} setShowModalListCase={setShowModalListCase}
          closeModal={closeModal} setSelectCase={setSelectCase} setTlpFilter={setTlpFilterCase}
          currentPage={currentPageCase} setCurrentPage={setCurrentPageCase}
          wordToSearch={wordToSearchCase} setWordToSearch={setWordToSearchCase}
          updatePagination={updatePaginationCase} setUpdatePagination={setUpdatePaginationCase}
          selectedCases={selectedCases} selectCase={selectCase}
          tlpNames={tlpNames} userNames={userNames} priorityNames={priorityNames}
          priorityFilter={priorityFilter} setPriorityFilter={setPriorityFilter}
          tlpFilter={tlpFilterCase} setStateFilter={setStateFilter} stateFilter={stateFilter}
          priorities={allPriorities} tlp={tlpList} allStates={states}
          handleClickRadio={handleClickRadio} caseToLink={caseToLink} modalCaseDetail={modalCaseDetail}
          linkCaseToEvent={linkCaseToEvent}
        />
        <ModalReadCase modalShowCase={modalShowCase} returnToListOfCases={returnToListOfCases} linkCaseToEvent={linkCaseToEvent} />
      </Card>
    </div>
  )
}
export default ListEvent