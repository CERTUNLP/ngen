import React, { useEffect, useState } from "react";
import { Card, Col, Form, Row } from "react-bootstrap";
import { getAudits } from "../../api/services/audit";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import TableAudit from "./components/TableAudit";
import Search from "../../components/Search/Search";
import { useTranslation } from "react-i18next";

const ACTION_OPTIONS = [
  { value: "", label: "All" },
  { value: "0", label: "Create" },
  { value: "1", label: "Update" },
  { value: "2", label: "Delete" },
];

const ListAudit = () => {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [order, setOrder] = useState("-timestamp");
  const [wordToSearch, setWordToSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [actorFilter, setActorFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  const buildFilters = () => {
    const parts = [];
    if (wordToSearch) parts.push(`search=${encodeURIComponent(wordToSearch)}`);
    if (actionFilter) parts.push(`action=${actionFilter}`);
    if (actorFilter) parts.push(`actor__username=${encodeURIComponent(actorFilter)}`);
    if (typeFilter) parts.push(`content_type__model=${encodeURIComponent(typeFilter)}`);
    if (dateFrom) parts.push(`timestamp_after=${encodeURIComponent(dateFrom)}`);
    if (dateTo) parts.push(`timestamp_before=${encodeURIComponent(dateTo)}`);
    return parts.join("&");
  };

  useEffect(() => {
    setLoading(true);
    getAudits(currentPage, buildFilters(), order)
      .then((response) => {
        setAudits(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) setUpdatePagination(true);
        setDisabledPagination(false);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [currentPage, wordToSearch, actionFilter, actorFilter, typeFilter, dateFrom, dateTo, order]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row className="g-2 align-items-end">
                <Col sm={12} lg={3}>
                  <Search
                    type={t("search.by.name.description")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                    setCurrentPage={setCurrentPage}
                  />
                </Col>
                <Col sm={6} lg={2}>
                  <Form.Group>
                    <Form.Label className="small mb-0">{t("w.action")}</Form.Label>
                    <Form.Select
                      size="sm"
                      value={actionFilter}
                      onChange={(e) => { setActionFilter(e.target.value); setCurrentPage(1); }}
                    >
                      {ACTION_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col sm={6} lg={2}>
                  <Form.Group>
                    <Form.Label className="small mb-0">{t("reporter")}</Form.Label>
                    <Form.Control
                      size="sm"
                      type="text"
                      value={actorFilter}
                      placeholder={t("reporter")}
                      onChange={(e) => { setActorFilter(e.target.value); setCurrentPage(1); }}
                    />
                  </Form.Group>
                </Col>
                <Col sm={6} lg={2}>
                  <Form.Group>
                    <Form.Label className="small mb-0">{t("ngen.type")}</Form.Label>
                    <Form.Control
                      size="sm"
                      type="text"
                      value={typeFilter}
                      placeholder={t("ngen.type")}
                      onChange={(e) => { setTypeFilter(e.target.value); setCurrentPage(1); }}
                    />
                  </Form.Group>
                </Col>
                <Col sm={6} lg={3}>
                  <Row className="g-1">
                    <Col xs={6}>
                      <Form.Group>
                        <Form.Label className="small mb-0">{t("date.condition_from")}</Form.Label>
                        <Form.Control
                          size="sm"
                          type="datetime-local"
                          value={dateFrom}
                          onChange={(e) => { setDateFrom(e.target.value); setCurrentPage(1); }}
                        />
                      </Form.Group>
                    </Col>
                    <Col xs={6}>
                      <Form.Group>
                        <Form.Label className="small mb-0">{t("date.condition_to")}</Form.Label>
                        <Form.Control
                          size="sm"
                          type="datetime-local"
                          value={dateTo}
                          onChange={(e) => { setDateTo(e.target.value); setCurrentPage(1); }}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
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
