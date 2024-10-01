import React, { useEffect, useState } from "react";
import { Card, Col, Row, Collapse } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import Alert from "../../components/Alert/Alert";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Navigation from "../../components/Navigation/Navigation";
import { getMinifiedTaxonomy, getTaxonomies } from "../../api/services/taxonomies";
import Search from "../../components/Search/Search";
import TableTaxonomy from "./components/TableTaxonomy";
import ButtonFilter from "../../components/Button/ButtonFilter";
import FilterSelectUrl from "../../components/Filter/FilterSelectUrl";
import FilterSelect from "../../components/Filter/FilterSelect";
import { useTranslation } from "react-i18next";
import { getMinifiedTaxonomyGroups } from "../../api/services/taxonomyGroups";

const ListTaxonomies = () => {
  const [taxonomies, setTaxonomies] = useState([]);
  const [taxonomyGroups, setTaxonomyGroups] = useState([]);
  const [minifiedTaxonomies, setMinifiedTaxonomies] = useState([]);
  const [isModify, setIsModify] = useState(null);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  const [showAlert, setShowAlert] = useState(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [wordToSearch, setWordToSearch] = useState("");

  // Filter data
  const [minifiedTaxonomiesParent, setMinifiedTaxonomiesParent] = useState([]);
  const [minifiedTaxonomyGroups, setMinifiedTaxonomyGroups] = useState([]);

  // Filters
  const [openFilter, setOpenFilter] = useState(false);
  const [typeFilter, setTypeFilter] = useState("");
  const [parentFilter, setParentFilter] = useState("");
  const [taxonomyGroupFilter, setTaxonomyGroupFilter] = useState("");
  const [aliasFilter, setAliasFilter] = useState("");
  const [needsReviewFilter, setNeedsReviewFilter] = useState("");
  const [reportsFilter, setReportsFilter] = useState("");
  const [activeFilter, setActiveFilter] = useState("");

  const [order, setOrder] = useState("name");

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getMinifiedTaxonomy().then((response) => {
      setMinifiedTaxonomiesParent(
        response.map((item) => ({
          value: item.url,
          label: item.name
        }))
      );
    });

    getMinifiedTaxonomyGroups().then((response) => {
      setMinifiedTaxonomyGroups(
        response.map((item) => ({
          value: item.url,
          label: item.name
        }))
      );
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    getMinifiedTaxonomyGroups()
      .then((response) => {
        let dicTaxonomyGroups = {};
        response.map((tg) => {
          dicTaxonomyGroups[tg.url] = tg.name;
          return null;
        });
        setTaxonomyGroups(dicTaxonomyGroups);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setLoading(false);
      });

    getMinifiedTaxonomy()
      .then((response) => {
        let dicMinifiedTaxonomy = {};
        response.map((tg) => {
          dicMinifiedTaxonomy[tg.url] = tg.name;
          return null;
        });
        setMinifiedTaxonomies(dicMinifiedTaxonomy);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setLoading(false);
      });

    getTaxonomies(currentPage, parentFilter + taxonomyGroupFilter + aliasFilter + typeFilter + needsReviewFilter + activeFilter + reportsFilter + wordToSearch, order)
      .then((response) => {
        setCountItems(response.data.count);
        setTaxonomies(response.data.results);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        //alert
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, isModify, order, wordToSearch, parentFilter, taxonomyGroupFilter, aliasFilter, typeFilter, activeFilter, needsReviewFilter, reportsFilter]);

  const optionsTaxonomyType = [
    { value: "vulnerability", label: t("ngen.vulnerability") },
    { value: "incident", label: t("ngen.incident") },
    { value: "other", label: t("ngen.other") },
  ];

  const optionsNeedsReview = [
    { value: "true", label: t("w.yes") },
    { value: "false", label: t("w.no") }
  ];

  const optionsActive = [
    { value: "true", label: t("w.yes") },
    { value: "false", label: t("w.no") }
  ];

  const optionsReports = [
    { value: "true", label: t("w.no") },
    { value: "false", label: t("w.yes") }
  ];

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="taxonomy" />

      <Row>
        <Navigation actualPosition={t("ngen.taxonomy_other")} />
      </Row>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={1} lg={1}>
                  <ButtonFilter open={openFilter} setOpen={setOpenFilter} />
                </Col>
                <Col sm={12} lg={8}>
                  <Search
                    type={t("search.by.name")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                  />
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton type="create" name={t("ngen.taxonomy_one")} to="/taxonomies/create" checkPermRoute />
                </Col>
              </Row>
              <br />
              <Collapse in={openFilter}>
                <div id="example-collapse-text">
                  <Row>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={minifiedTaxonomiesParent}
                        itemName={t("ngen.taxonomy.parent")}
                        partOfTheUrl="parent"
                        itemFilter={parentFilter}
                        itemFilterSetter={setParentFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={minifiedTaxonomyGroups}
                        itemName={t("ngen.taxonomy.group")}
                        partOfTheUrl="group"
                        itemFilter={taxonomyGroupFilter}
                        itemFilterSetter={setTaxonomyGroupFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={minifiedTaxonomiesParent}
                        itemName={t("ngen.taxonomy.alias_of")}
                        partOfTheUrl="alias_of"
                        itemFilter={aliasFilter}
                        itemFilterSetter={setAliasFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                  </Row>
                  <br />
                  <Row>
                    <Col sm={4} lg={4}>
                      <FilterSelect
                        options={optionsTaxonomyType}
                        partOfTheUrl="type"
                        setFilter={setTypeFilter}
                        currentFilter={typeFilter}
                        setLoading={setLoading}
                        placeholder={t("ngen.filter_by") + " " + t("ngen.type")}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelect
                        options={optionsNeedsReview}
                        itemName={t("ngen.taxonomy.needs_review")}
                        partOfTheUrl="needs_review"
                        setFilter={setNeedsReviewFilter}
                        currentFilter={needsReviewFilter}
                        setLoading={setLoading}
                        placeholder={t("ngen.filter_by") + " " + t("ngen.taxonomy.needs_review")}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelect
                        options={optionsActive}
                        itemName={t("w.active")}
                        partOfTheUrl="active"
                        setFilter={setActiveFilter}
                        currentFilter={activeFilter}
                        setLoading={setLoading}
                        placeholder={t("ngen.filter_by") + " " + t("w.active")}
                      />
                    </Col>
                  </Row>
                  <br />
                  <Row>
                    <Col sm={4} lg={4}>
                      <FilterSelect
                        options={optionsReports}
                        itemName={t("ngen.report_other")}
                        partOfTheUrl="reports__isnull"
                        setFilter={setReportsFilter}
                        currentFilter={reportsFilter}
                        setLoading={setLoading}
                        placeholder={t("ngen.filter_by") + " " + t("ngen.report_other")}
                      />
                    </Col>
                  </Row>
                </div>
              </Collapse>
            </Card.Header>
            <Card.Body>
              <TableTaxonomy
                setIsModify={setIsModify}
                list={taxonomies}
                loading={loading}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                taxonomyGroups={taxonomyGroups}
                minifiedTaxonomies={minifiedTaxonomies}
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

export default ListTaxonomies;
