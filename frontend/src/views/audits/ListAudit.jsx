import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { getAudits } from "../../api/services/audit";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import TableAudit from "./components/TableAudit";
import Search from "../../components/Search/Search";
import { useTranslation } from "react-i18next";

const ListAudit = () => {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [order, setOrder] = useState("-timestamp");
  const [wordToSearch, setWordToSearch] = useState("");
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getAudits(currentPage, wordToSearch, order)
      .then((response) => {
        setAudits(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) setUpdatePagination(true);
        setDisabledPagination(false);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [currentPage, wordToSearch, order]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={12}>
                  <Search
                    type={t("search.by.name.description")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                    setCurrentPage={setCurrentPage}
                  />
                </Col>
              </Row>
            </Card.Header>
            <TableAudit
              audits={audits}
              loading={loading}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
            />
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

export default ListAudit;
