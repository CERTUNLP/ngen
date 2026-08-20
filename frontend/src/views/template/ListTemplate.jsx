import React, { useEffect, useState } from "react";
import { Card, Col, Collapse, Row } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import TableTemplete from "./components/TableTemplete";
import ListViewHeader from "../../components/ListViewHeader/ListViewHeader";
import { getTemplates } from "../../api/services/templates";
import { getMinifiedFeed } from "../../api/services/feeds";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Alert from "../../components/Alert/Alert";
import FilterSelectUrl from "../../components/Filter/FilterSelectUrl";
import { useTranslation } from "react-i18next";
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedPriority } from "../../api/services/priorities";
import { getMinifiedState } from "../../api/services/states";

const ListTemplete = () => {
  const [templete, setTemplete] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [isModify, setIsModify] = useState(null);
  const { t } = useTranslation();

  const [showAlert, setShowAlert] = useState(false);
  const [open, setOpen] = useState(false);

  const [taxonomies, setTaxonomies] = useState([]);
  const [feeds, setFeeds] = useState([]);
  // const [priorities, setPriorities] = useState([])
  // const [tlps, setTlps] = useState([])
  // const [states, setStates] = useState([])

  const [taxonomyFilter, setTaxonomyFilter] = useState("");
  const [feedFilter, setFeedFilter] = useState("");
  const [wordToSearch, setWordToSearch] = useState("");
  const [valueFeedFilter, setValueFeedFilter] = useState(null);
  const [valueTaxonomyFilter, setValueTaxonomyFilter] = useState(null);
  const [order, setOrder] = useState("event_feed__name");
  const [refresh, setRefresh] = useState(true);

  const [taxonomyNames, setTaxonomyNames] = useState({});
  const [feedNames, setFeedNames] = useState({});
  const [priorityNames, setPriorityNames] = useState({});
  const [tlpNames, setTlpNames] = useState({});
  const [stateNames, setStateNames] = useState({});

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  const reloadPage = () => {
    setLoading(true);
    setRefresh((prev) => !prev);
  };

  const clearFilters = () => {
    setLoading(true);
    setWordToSearch("");
    setTaxonomyFilter("");
    setValueTaxonomyFilter(null);
    setFeedFilter("");
    setValueFeedFilter(null);
    setCurrentPage(1);
    setRefresh((prev) => !prev);
  };

  useEffect(() => {
    getMinifiedTaxonomy().then((response) => {
      let listTaxonomies = [];
      let dicTaxonomy = {};
      response.forEach((taxonomy) => {
        listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name });
        dicTaxonomy[taxonomy.url] = taxonomy.name;
      });
      setTaxonomyNames(dicTaxonomy);
      setTaxonomies(listTaxonomies);
    });

    getMinifiedTlp().then((response) => {
      let listTlps = [];
      let dicTlp = {};
      response.forEach((tlp) => {
        listTlps.push({ value: tlp.url, label: tlp.name });
        dicTlp[tlp.url] = tlp.name;
      });
      setTlpNames(dicTlp);
      // setTlps(listTlps)
    });

    getMinifiedPriority().then((response) => {
      let listPriorities = [];
      let dicPriority = {};
      response.forEach((priority) => {
        listPriorities.push({ value: priority.url, label: priority.name });
        dicPriority[priority.url] = priority.name;
      });
      setPriorityNames(dicPriority);
      // setPriorities(listPriorities)
    });

    getMinifiedState().then((response) => {
      let listStates = [];
      let dicState = {};
      response.forEach((state) => {
        listStates.push({ value: state.url, label: state.name });
        dicState[state.url] = state.name;
      });
      setStateNames(dicState);
      // setStates(listStates)
    });

    getMinifiedFeed().then((response) => {
      let listFeeds = [];
      let dicFeed = {};
      response.forEach((feed) => {
        listFeeds.push({ value: feed.url, label: feed.name });
        dicFeed[feed.url] = feed.name;
      });
      setFeedNames(dicFeed);
      setFeeds(listFeeds);
    });

    getTemplates(currentPage, taxonomyFilter + feedFilter + wordToSearch, order)
      .then((response) => {
        setTemplete(response.data.results);
        setCountItems(response.data.count);
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, taxonomyFilter, feedFilter, wordToSearch, order, isModify, refresh]);

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm="auto">
          <Card>
            <Card.Header>
              <ListViewHeader
                open={open}
                setOpen={setOpen}
                searchType={t("cidr.domain")}
                wordToSearch={wordToSearch}
                setWordToSearch={setWordToSearch}
                setLoading={setLoading}
                setCurrentPage={setCurrentPage}
                onReload={reloadPage}
                onClearFilters={clearFilters}
              >
                <CrudButton type="create" name={t("ngen.template")} to="/templates/create" checkPermRoute />
              </ListViewHeader>
              <Collapse in={open}>
                <div id="example-collapse-text">
                  <Row>
                    <Col sm={12} lg={4}>
                      <FilterSelectUrl
                        options={feeds}
                        itemName={t("ngen.feed_other")}
                        partOfTheUrl="event_feed"
                        itemFilter={feedFilter}
                        itemFilterSetter={setFeedFilter}
                        value={valueFeedFilter}
                        setValue={setValueFeedFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                    <Col sm={12} lg={4}>
                      <FilterSelectUrl
                        options={taxonomies}
                        itemName={t("ngen.taxonomy_one")}
                        partOfTheUrl="event_taxonomy"
                        itemFilter={taxonomyFilter}
                        itemFilterSetter={setTaxonomyFilter}
                        value={valueTaxonomyFilter}
                        setValue={setValueTaxonomyFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                  </Row>
                </div>
              </Collapse>
            </Card.Header>
            <Card.Body>
              <TableTemplete
                list={templete}
                loading={loading}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                currentPage={currentPage}
                taxonomyNames={taxonomyNames}
                feedNames={feedNames}
                tlpNames={tlpNames}
                priorityNames={priorityNames}
                stateNames={stateNames}
                setIsModify={setIsModify}
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
                    setDisabledPagination={setDisabledPagination}
                    disabledPagination={disabledPagination}
                  />
                </Col>
              </Row>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default ListTemplete;
