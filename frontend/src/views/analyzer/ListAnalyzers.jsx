import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Search from "../../components/Search/Search";
import TableAnalyzer from "./components/TableAnalyzer";
import FilterToolbar from "../../components/Button/FilterToolbar";
import { useTranslation } from "react-i18next";
import { getAnalyzers } from "../../api/services/analyzer";

const ListAnalyzers = () => {
  const [analyzers, setAnalyzers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [wordToSearch, setWordToSearch] = useState("");
  const [order, setOrder] = useState("name");
  const [refreshKey, setRefreshKey] = useState(0);
  const [refresh, setRefresh] = useState(true);

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
    setCurrentPage(1);
    setRefresh((prev) => !prev);
  };

  useEffect(() => {
    setLoading(true);
    getAnalyzers(currentPage, wordToSearch, order)
      .then((response) => {
        setCountItems(response.data.count);
        setAnalyzers(response.data.results);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => console.error(error))
      .finally(() => setLoading(false));
  }, [currentPage, order, wordToSearch, refreshKey, refresh]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm="auto">
                  <FilterToolbar onReload={reloadPage} onClearFilters={clearFilters} />
                </Col>
                <Col sm={12} lg={8}>
                  <Search
                    type={t("search.by.name")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                    setCurrentPage={setCurrentPage}
                  />
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton
                    type="create"
                    name={t("ngen.analyzer.one")}
                    to="/analyzers/create"
                    checkPermRoute
                  />
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <TableAnalyzer
                list={analyzers}
                loading={loading}
                order={order}
                setOrder={setOrder}
                onDeleted={() => setRefreshKey((k) => k + 1)}
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

export default ListAnalyzers;