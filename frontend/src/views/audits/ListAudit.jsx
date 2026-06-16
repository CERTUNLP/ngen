import React, { useEffect, useState } from "react";
import { Card, Col, Collapse, Form, Row } from "react-bootstrap";
import { getAudits } from "../../api/services/audit";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import TableAudit from "./components/TableAudit";
import Search from "../../components/Search/Search";
import FilterToolbar from "../../components/Button/FilterToolbar";
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
  const [open, setOpen] = useState(false);
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

  const clearFilters = () => {
    setActionFilter("");
    setActorFilter("");
    setTypeFilter("");
    setDateFrom("");
    setDateTo("");
    setCurrentPage(1);
  };

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm="auto">
                  <FilterToolbar open={open} setOpen={setOpen} onReload={() => setCurrentPage(1)} onClearFilters={clearFilters} />
                </Col>
                <Col sm={8} lg={4}>
                  <Search
                    type={t("search.by.name.description")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                    setCurrentPage={setCurrentPage}
                  />
                </Col>
              </Row>
              <Collapse in={open}>
                <div id="example-collapse-text">
                  <Row>
                    <Col sm={12} lg={6}>
                      <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t("date.condition_from")}</Form.Label>
                        <Form.Control
                          type="date"
                          maxLength="150"
                          placeholder={t("date.condition_from")}
                          value={dateFrom}
                          onChange={(e) => { setDateFrom(e.target.value); setCurrentPage(1); }}
                          name="date"
                        />
                      </Form.Group>
                    </Col>
                    <Col sm={12} lg={6}>
                      <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t("date.condition_to")}</Form.Label>
                        <Form.Control
                          type="date"
                          maxLength="150"
                          value={dateTo}
                          onChange={(e) => { setDateTo(e.target.value); setCurrentPage(1); }}
                          name="date"
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  <Row>
                    <Col sm={4} lg={4}>
                      <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t("w.action")}</Form.Label>
                        <Form.Select
                          value={actionFilter}
                          onChange={(e) => { setActionFilter(e.target.value); setCurrentPage(1); }}
                          name="action"
                        >
                          {ACTION_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col sm={4} lg={4}>
                      <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t("reporter")}</Form.Label>
                        <Form.Control
                          type="text"
                          maxLength="150"
                          value={actorFilter}
                          placeholder={t("reporter")}
                          onChange={(e) => { setActorFilter(e.target.value); setCurrentPage(1); }}
                          name="reporter"
                        />
                      </Form.Group>
                    </Col>
                    <Col sm={4} lg={4}>
                      <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t("ngen.type")}</Form.Label>
                        <Form.Control
                          type="text"
                          maxLength="150"
                          value={typeFilter}
                          placeholder={t("ngen.type")}
                          onChange={(e) => { setTypeFilter(e.target.value); setCurrentPage(1); }}
                          name="type"
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                </div>
              </Collapse>
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
