import React, { useState } from "react";
import { Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import { Link } from "react-router-dom";
import ActiveButton from "../../../components/Button/ActiveButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import { createCases, deleteTemplate, isActive } from "../../../api/services/templates";
import Alert from "../../../components/Alert/Alert";
import Ordering from "../../../components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const TableTemplete = ({
  list,
  loading,
  order,
  setOrder,
  setLoading,
  currentPage,
  taxonomyNames,
  feedNames,
  tlpNames,
  priorityNames,
  stateNames
}) => {
  const [deleteName, setDeleteName] = useState();
  const [deleteUrl, setDeleteUrl] = useState();
  const [id, setId] = useState("");
  const [remove, setRemove] = useState();
  const [template, setTemplate] = useState({});
  const [modalShow, setModalShow] = useState(false);
  const [dataTemplate, setDataTemplate] = useState({});
  const [showTemplate, setShowTemplate] = useState();
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const modalDelete = (cidr, domain, taxonomy, feed, url) => {
    let name = "[" + (cidr || domain) + " - " + taxonomy + " - " + feed + "]";
    setDeleteName(name);
    setDeleteUrl(url);
    setRemove(true);
  };

  const handleDelete = () => {
    deleteTemplate(deleteUrl)
      .then(() => {
        window.location.href = "/templates";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setRemove(false);
      });
  };

  const showModalTemplate = (template) => {
    setId(template.url.split("/")[template.url.split("/").length - 2]);
    setTemplate(template);
    setModalShow(true);
  };

  const modalChangeState = (url, cidr, domain, taxonomy, feed, active) => {
    let name = "[" + (cidr || domain) + " - " + taxonomy + " - " + feed + "]";
    setDataTemplate({ url: url, name: name, state: active });
    setShowTemplate(true);
  };

  const create = (url) => {
    createCases(url)
      .then(() => {
        window.location.href = "/templates";
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const changeState = () => {
    isActive(dataTemplate.url, +!dataTemplate.state)
      .then(() => {
        window.location.href = "/templates";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setShowTemplate(false);
      });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };
  const letterSize = { fontSize: "1.1em" };
  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />

      <ul className="list-group my-4">
        <Table responsive hover className="text-center">
          <thead>
            <tr>
              <Ordering
                field="cidr,domain"
                label={t("ngen.affectedResources")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="event_taxonomy__name"
                label={t("ngen.taxonomy_one")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="event_feed__name"
                label={t("ngen.feed.information")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="active"
                label={t("w.active")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="priority"
                label={t("ngen.priority_one")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="case_state"
                label={t("ngen.state_one")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="case_tlp"
                label={t("ngen.tlp")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="matching_events_without_case_count"
                label={t("ngen.template.matching_events_without_case")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <th>{t("ngen.options")}</th>
            </tr>
          </thead>
          <tbody>
            {list.map((template, index) => {
              const parts = template.url.split("/");
              let itemNumber = parts[parts.length - 2];
              return (
                <tr key={index}>
                  <td>{template.cidr || template.domain}</td>
                  <td>{taxonomyNames[template.event_taxonomy]}</td>
                  <td>{feedNames[template.event_feed]}</td>
                  <td>
                    <ActiveButton
                      active={+template.active}
                      onClick={() =>
                        modalChangeState(
                          template.url,
                          template.cidr,
                          template.domain,
                          taxonomyNames[template.event_taxonomy],
                          feedNames[template.event_feed],
                          template.active
                        )
                      }
                    />
                  </td>
                  <td>{priorityNames[template.priority]}</td>
                  <td>{stateNames[template.case_state]}</td>
                  <td>{tlpNames[template.case_tlp]}</td>
                  <td>
                    {template.matching_events_without_case_count > 0 ? (
                      <Button
                        className=""
                        variant="outline-primary"
                        onClick={() => create(template.url)}
                        style={{
                          borderRadius: "50px"
                        }}
                      >
                        {template.matching_events_without_case_count}
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-play"
                          viewBox="-2 2 16 16"
                        >
                          <path d="M12.645 8.235l-6.647-4.662a1 1 0 0 0-1.618.785v9.324a1 1 0 0 0 1.618.785l6.647-4.662a1 1 0 0 0 0-1.57z" />
                        </svg>
                      </Button>
                    ) : (
                      <Button
                        disabled
                        className=""
                        variant="outline-secundary"
                        style={{
                          border: "1px solid #555",
                          borderRadius: "50px",
                          color: "#555"
                        }}
                      >
                        {template.matching_events_without_case_count}
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-play"
                          viewBox="-2 2 16 16"
                        >
                          <path d="M12.645 8.235l-6.647-4.662a1 1 0 0 0-1.618.785v9.324a1 1 0 0 0 1.618.785l6.647-4.662a1 1 0 0 0 0-1.57z" />
                        </svg>
                      </Button>
                    )}
                  </td>
                  <td>
                    <CrudButton type="read" onClick={() => showModalTemplate(template)} />
                    <Link to={`/templates/edit/${itemNumber}`}>
                      <CrudButton type="edit" />
                    </Link>
                    <CrudButton
                      type="delete"
                      onClick={() =>
                        modalDelete(
                          template.cidr,
                          template.domain,
                          taxonomyNames[template.event_taxonomy],
                          feedNames[template.event_feed],
                          template.url
                        )
                      }
                    />
                  </td>
                </tr>
              );
            })}

            <ModalConfirm
              type="delete"
              component={t("ngen.state_one")}
              name={deleteName}
              showModal={remove}
              onHide={() => setRemove(false)}
              ifConfirm={() => handleDelete(deleteUrl)}
            />
            <ModalConfirm
              type="editState"
              component={t("ngen.state_one")}
              name={dataTemplate.cidr || dataTemplate.domain}
              state={dataTemplate.state}
              showModal={showTemplate}
              onHide={() => setShowTemplate(false)}
              ifConfirm={() => changeState()}
            />
            <Modal size="lg" show={modalShow} onHide={() => setModalShow(false)} aria-labelledby="contained-modal-title-vcenter" centered>
              <Modal.Body>
                <Row>
                  <Col>
                    <Card>
                      <Card.Header>
                        <Row>
                          <Col>
                            <Card.Title as="h5">{t("ngen.template")}</Card.Title>
                            <span className="d-block m-t-5">{t("ngen.template.detail")}</span>
                          </Col>
                          <Col sm={12} lg={4}>
                            <Link to={`/templates/edit/${id}`}>
                              <CrudButton type="edit" />
                            </Link>
                            <CloseButton aria-label={t("w.close")} onClick={() => setModalShow(false)} />
                          </Col>
                        </Row>
                      </Card.Header>
                      <Card.Body>
                        <Table responsive>
                          <tr>
                            <td>{t("ngen.cidr")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={template.cidr} />
                            </td>
                            <td></td>
                          </tr>
                          <tr>
                            <td>{t("ngen.domain")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={template.domain} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.lifecycle_one")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={template.case_lifecycle} />
                            </td>
                          </tr>

                          <tr>
                            <td>{t("w.active")}</td>
                            <td>
                              <Button
                                className="btn-icon btn-rounded"
                                variant={template.active ? "outline-success" : "outline-danger"}
                                title={template.active ? "Activo" : "Inactivo"}
                              >
                                <i className={template.active ? "feather icon-check-circle" : "feather icon-alert-triangle"} />
                              </Button>
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.date.created")}</td>
                            <td>
                              <Form.Control
                                plaintext
                                readOnly
                                defaultValue={template.created ? template.created.slice(0, 10) + " " + template.created.slice(11, 19) : ""}
                              />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.date.modified")}</td>
                            <td>
                              <Form.Control
                                plaintext
                                readOnly
                                defaultValue={
                                  template.modified ? template.modified.slice(0, 10) + " " + template.modified.slice(11, 19) : ""
                                }
                              />
                            </td>
                          </tr>
                        </Table>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Modal.Body>
            </Modal>
          </tbody>
        </Table>
      </ul>
    </React.Fragment>
  );
};

export default TableTemplete;
