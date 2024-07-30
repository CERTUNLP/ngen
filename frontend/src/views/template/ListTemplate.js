import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Row, Col, Card, Collapse } from 'react-bootstrap';
import CrudButton from '../../components/Button/CrudButton';
import TableTemplete from './components/TableTemplete';
import Navigation from '../../components/Navigation/Navigation';
import Search from '../../components/Search/Search'
import { getTemplates } from '../../api/services/templates';
import { getMinifiedFeed } from "../../api/services/feeds";
import { getMinifiedTaxonomy } from '../../api/services/taxonomies';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import Alert from '../../components/Alert/Alert';
import ButtonFilter from '../../components/Button/ButtonFilter';
import FilterSelectUrl from '../../components/Filter/FilterSelectUrl';
import { useTranslation, Trans } from 'react-i18next';
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedPriority } from "../../api/services/priorities";
import { getMinifiedState } from "../../api/services/states";

const ListTemplete = () => {
    const [templete, setTemplete] = useState([])
    const [loading, setLoading] = useState(true)
    const [currentPage, setCurrentPage] = useState(1)
    const [countItems, setCountItems] = useState(0);
    const [updatePagination, setUpdatePagination] = useState(false)
    const [disabledPagination, setDisabledPagination] = useState(true)
    const { t } = useTranslation();

    const [showAlert, setShowAlert] = useState(false)
    const [open, setOpen] = useState(false);

    const [taxonomies, setTaxonomies] = useState([]);
    const [feeds, setFeeds] = useState([])
    const [priorities, setPriorities] = useState([])
    const [tlps, setTlps] = useState([])
    const [states, setStates] = useState([])

    const [taxonomyFilter, setTaxonomyFilter] = useState('')
    const [feedFilter, setFeedFilter] = useState('')
    const [wordToSearch, setWordToSearch] = useState('')
    const [order, setOrder] = useState("event_feed__name");

    const [taxonomyNames, setTaxonomyNames] = useState({});
    const [feedNames, setFeedNames] = useState({});
    const [priorityNames, setPriorityNames] = useState({});
    const [tlpNames, setTlpNames] = useState({});
    const [stateNames, setStateNames] = useState({});
    function updatePage(chosenPage) {
        setCurrentPage(chosenPage);
    }


    useEffect(() => {

        getMinifiedTaxonomy()
            .then((response) => {
                let listTaxonomies = []
                let dicTaxonomy = {}
                response.map((taxonomy) => {
                    listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name })
                    dicTaxonomy[taxonomy.url] = taxonomy.name
                })
                setTaxonomyNames(dicTaxonomy)
                setTaxonomies(listTaxonomies)
            })

        getMinifiedTlp()
            .then((response) => {
                let listTlps = []
                let dicTlp = {}
                response.map((tlp) => {
                    listTlps.push({ value: tlp.url, label: tlp.name })
                    dicTlp[tlp.url] = tlp.name
                })
                setTlpNames(dicTlp)
                setTlps(listTlps)
            })

        getMinifiedPriority()
            .then((response) => {
                let listPriorities = []
                let dicPriority = {}
                response.map((priority) => {
                    listPriorities.push({ value: priority.url, label: priority.name })
                    dicPriority[priority.url] = priority.name
                })
                setPriorityNames(dicPriority)
                setPriorities(listPriorities)
            })

        getMinifiedState()
            .then((response) => {
                let listStates = []
                let dicState = {}
                response.map((state) => {
                    listStates.push({ value: state.url, label: state.name })
                    dicState[state.url] = state.name
                })
                setStateNames(dicState)
                setStates(listStates)
            })

        getMinifiedFeed().then((response) => {
            let listFeeds = []
            let dicFeed = {}
            response.map((feed) => {
                listFeeds.push({ value: feed.url, label: feed.name })
                dicFeed[feed.url] = feed.name
            })
            setFeedNames(dicFeed)
            setFeeds(listFeeds)
        })

        getTemplates(currentPage, taxonomyFilter + feedFilter + wordToSearch, order)
            .then((response) => {
                setTemplete(response.data.results);
                setCountItems(response.data.count)
                setCountItems(response.data.count)
                if (currentPage === 1) {
                    setUpdatePagination(true)
                }
                setDisabledPagination(false)
            })
            .catch((error) => {
                console.log(error)
            })
            .finally(() => {
                setShowAlert(true)
                setLoading(false)
            })

    }, [currentPage, taxonomyFilter, feedFilter, wordToSearch, order])

    const resetShowAlert = () => {
        setShowAlert(false);
    }

    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="template" />
            <Row>
                <Navigation actualPosition={t('ngen.template')} />
            </Row>
            <Row>
                <Col>
                    <Card>
                        <Card.Header>
                            <Row>
                                <Col sm={1} lg={1}>
                                    <ButtonFilter open={open} setOpen={setOpen} />
                                </Col>
                                <Col sm={12} lg={8}>
                                    <Search type={t('cidr.domain')} setWordToSearch={setWordToSearch} wordToSearch={wordToSearch} setLoading={setLoading} />
                                </Col>
                                <Col sm={12} lg={3}>
                                    <Link to={{ pathname: '/templates/create' }} >
                                        <CrudButton type='create' name={t('ngen.template')} />
                                    </Link>
                                </Col>
                            </Row>
                            <Collapse in={open}>
                                <div id="example-collapse-text">
                                    <br />
                                    <Row>
                                        <Col sm={12} lg={4}>
                                            <FilterSelectUrl options={feeds} itemName={t('ngen.feed_other')} partOfTheUrl="event_feed" itemFilter={feedFilter} itemFilterSetter={setFeedFilter} setLoading={setLoading} />
                                        </Col>
                                        <Col sm={12} lg={4}>
                                            <FilterSelectUrl options={taxonomies} itemName={t('ngen.taxonomy_one')} partOfTheUrl="event_taxonomy" itemFilter={taxonomyFilter} itemFilterSetter={setTaxonomyFilter} setLoading={setLoading} />
                                        </Col>

                                    </Row>
                                    <br />
                                </div>
                            </Collapse>
                        </Card.Header>
                        <Card.Body>
                            <TableTemplete list={templete} loading={loading} order={order} setOrder={setOrder} setLoading={setLoading} currentPage={currentPage}
                                taxonomyNames={taxonomyNames} feedNames={feedNames} tlpNames={tlpNames} priorityNames={priorityNames} stateNames={stateNames} />
                        </Card.Body>
                        <Card.Footer >
                            <Row className="justify-content-md-center">
                                <Col md="auto">
                                    <AdvancedPagination countItems={countItems} updatePage={updatePage} updatePagination={updatePagination} setUpdatePagination={setUpdatePagination} setLoading={setLoading} setDisabledPagination={setDisabledPagination} disabledPagination={disabledPagination} />
                                </Col>
                            </Row>
                        </Card.Footer>
                    </Card>
                </Col>
            </Row>
        </React.Fragment>
    )
}

export default ListTemplete