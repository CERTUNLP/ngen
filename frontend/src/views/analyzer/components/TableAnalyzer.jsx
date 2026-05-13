import React, { useState } from "react";
import { Badge, Card, CloseButton, Col, Modal, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import DateShowField from "../../../components/Field/DateShowField";
import { useTranslation } from "react-i18next";
import { deleteAnalyzer, testAnalyzerConnection } from "../../../api/services/analyzer";
import setAlert from "../../../utils/setAlert";

const SENSITIVE_PLACEHOLDER = "********";

const getConfigFieldLabel = (field, t) => {
  const key = `ngen.analyzer.config_fields.${field}`;
  const translated = t(key);
  return translated === key ? field : translated;
};

const TableAnalyzer = ({ list, loading, order, setOrder, onDeleted }) => {
  const [modalDelete, setModalDelete] = useState(false);
  const [modalShow, setModalShow] = useState(false);
  const [selectedAnalyzer, setSelectedAnalyzer] = useState(null);
  const [testingUrl, setTestingUrl] = useState(null);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleShowDetail = (analyzer) => {
    setSelectedAnalyzer(analyzer);
    setModalShow(true);
  };

  const handleDelete = () => {
    deleteAnalyzer(selectedAnalyzer.url, selectedAnalyzer.name)
      .then(() => {
        setModalDelete(false);
        onDeleted();
      })
      .catch((error) => console.error(error));
  };

  const handleTest = (analyzer) => {
    setTestingUrl(analyzer.url);
    testAnalyzerConnection(analyzer.url)
      .then((response) => {
        const msg = response.data.message || t("ngen.analyzer.test.ok");
        setAlert(msg, "success", "analyzer");
      })
      .catch((error) => {
        const msg = error.response?.data?.message || t("ngen.analyzer.test.fail");
        setAlert(msg, "error", "analyzer");
      })
      .finally(() => setTestingUrl(null));
  };

  const renderConfigValue = (key, value, schema) => {
    if (schema && schema[key] && schema[key].sensitive) return SENSITIVE_PLACEHOLDER;
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  };

  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <th>{t("ngen.name_one")}</th>
            <th>{t("ngen.analyzer.type")}</th>
            <th>{t("w.active")}</th>
            <th>{t("ngen.date.created")}</th>
            <th>{t("ngen.options")}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((analyzer, index) => {
            const parts = analyzer.url.split("/");
            const itemNumber = parts[parts.length - 2];
            return (
              <tr key={index}>
                <td>{analyzer.name}</td>
                <td>
                  <Badge bg="secondary">{analyzer.type}</Badge>
                </td>
                <td>
                  <Badge bg={analyzer.enabled ? "success" : "danger"}>
                    {analyzer.enabled ? t("w.yes") : t("w.no")}
                  </Badge>
                </td>
                <td>
                  <DateShowField value={analyzer.created} />
                </td>
                <td>
                  <CrudButton type="read" onClick={() => handleShowDetail(analyzer)} />
                  <CrudButton type="edit" to={`/analyzers/edit/${itemNumber}`} checkPermRoute />
                  <CrudButton
                    type="check"
                    onClick={() => handleTest(analyzer)}
                    disabled={testingUrl === analyzer.url || !analyzer.enabled}
                    title={t("ngen.analyzer.test_connection")}
                  />
                  <CrudButton
                    type="delete"
                    onClick={() => { setSelectedAnalyzer(analyzer); setModalDelete(true); }}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>

      {/* Detail modal */}
      <Modal size="lg" show={modalShow} onHide={() => setModalShow(false)} centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("ngen.analyzer.detail")}</Card.Title>
                    </Col>
                    <Col sm={12} lg={2}>
                      <CloseButton onClick={() => setModalShow(false)} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      <tr>
                        <td>{t("ngen.name_one")}</td>
                        <td>{selectedAnalyzer?.name}</td>
                      </tr>
                      <tr>
                        <td>{t("ngen.analyzer.type")}</td>
                        <td><Badge bg="secondary">{selectedAnalyzer?.type}</Badge></td>
                      </tr>
                      <tr>
                        <td>{t("w.active")}</td>
                        <td>
                          <Badge bg={selectedAnalyzer?.enabled ? "success" : "danger"}>
                            {selectedAnalyzer?.enabled ? t("w.yes") : t("w.no")}
                          </Badge>
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.description")}</td>
                        <td>{selectedAnalyzer?.description || "-"}</td>
                      </tr>
                      {selectedAnalyzer?.config && Object.entries(selectedAnalyzer.config).map(([key, value]) => (
                        <tr key={key}>
                          <td>{getConfigFieldLabel(key, t)}</td>
                          <td>{renderConfigValue(key, value, selectedAnalyzer.config_schema)}</td>
                        </tr>
                      ))}
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td><DateShowField value={selectedAnalyzer?.created} /></td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td><DateShowField value={selectedAnalyzer?.modified} /></td>
                      </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>

      {/* Delete confirmation modal */}
      <ModalConfirm
        type="delete"
        component={t("ngen.analyzer.one")}
        name={selectedAnalyzer?.name}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={handleDelete}
      />
    </React.Fragment>
  );
};

export default TableAnalyzer;