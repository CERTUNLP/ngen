import React, { useState } from "react";
import { Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import { deletePriority } from "api/services/priorities";
import CrudButton from "components/Button/CrudButton";
import ModalConfirm from "components/Modal/ModalConfirm";
import Alert from "components/Alert/Alert";
import Ordering from "components/Ordering/Ordering";
import DateShowField from "components/Field/DateShowField";
import { useTranslation } from "react-i18next";

const TablePriorities = ({ Priorities, loading, order, setOrder, setLoading, currentPage }) => {
  const [remove, setRemove] = useState(false);
  const [deleteName, setDeleteName] = useState("");
  const [id, setId] = useState("");
  const [deleteUrl, setDeleteUrl] = useState("");
  const [priority, setPriority] = useState({});
  const [modalShow, setModalShow] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleShow = (name, url) => {
    setDeleteName(name);
    setDeleteUrl(url);
    setRemove(true);
  };

  const handleDelete = () => {
    deletePriority(deleteUrl)
      .then(() => {
        window.location.href = "/priorities";
      })
      .catch((error) => {
        setRemove(false);
        setShowAlert(true);
        console.log(error);
      });
  };
  const showModalPriority = (priority) => {
    setId(priority.url.split("/")[priority.data.url.split("/").length - 2]);
    setPriority(priority);
    setModalShow(true);
  };

  const letterSize = { fontSize: "1.1em" };
  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />

      <ul className="list-group my-4">
        <Table responsive hover className="text-center">
          <thead>
            <tr>
              <Ordering
                field="name"
                label={t("ngen.name_one")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <th style={letterSize}>{t("date.limit.response")}</th>
              <th style={letterSize}>{t("date.limit.resolution")}</th>
              <th style={letterSize}>{t("ngen.priority.severity")}</th>
              <th style={letterSize}>{t("ngen.priority.notification_amount")}</th>
              <th style={letterSize}>{t("ngen.priority.color")}</th>
              <th style={letterSize}>{t("ngen.options")}</th>
            </tr>
          </thead>
          <tbody>
            {Priorities.map((priority, index) => {
              const parts = priority.url.split("/");
              let itemNumber = parts[parts.length - 2];
              return (
                <tr key={index}>
                  <td>{priority.name}</td>
                  <td>{priority.attend_time}</td>
                  <td>{priority.solve_time}</td>
                  <td>{priority.severity}</td>
                  <td>{priority.notification_amount}</td>
                  <td>{priority.color}</td>
                  <td>
                    <CrudButton
                      type="read"
                      onClick={() => {
                        showModalPriority(priority);
                      }}
                    />

                    <CrudButton type="edit" to={`/priorities/edit/${itemNumber}`} checkPermRoute />
                    <CrudButton type="delete" onClick={() => handleShow(priority.name, priority.url)} permissions="delete_priority" />
                  </td>
                </tr>
              );
            })}
            <Modal size="lg" show={modalShow} onHide={() => setModalShow(false)} aria-labelledby="contained-modal-title-vcenter" centered>
              <Modal.Body>
                <Row>
                  <Col>
                    <Card>
                      <Card.Header>
                        <Row>
                          <Col>
                            <Card.Title as="h5">{t("ngen.priority_one")}</Card.Title>
                            <span className="d-block m-t-5">{t("ngen.priority.detail")}</span>
                          </Col>
                          <Col sm={12} lg={4}>
                            <CrudButton type="edit" to={`/priorities/edit/${id}`} checkPermRoute />
                            <CloseButton aria-label={t("w.close")} onClick={() => setModalShow(false)} />
                          </Col>
                        </Row>
                      </Card.Header>
                      <Card.Body>
                        <Table responsive>
                          <tr>
                            <td>{t("ngen.name_one")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={priority.name} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("date.limit.response")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={priority.attend_time} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("date.limit.resolution")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={priority.solve_time} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.priority.severity")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={priority.severity} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.priority.color")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={priority.color} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.priority.notification_amount")}</td>
                            <td>
                              <Form.Control plaintext readOnly defaultValue={priority.notification_amount} />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.date.created")}</td>
                            <td>
                              <DateShowField value={priority?.created} asFormControl />
                            </td>
                          </tr>
                          <tr>
                            <td>{t("ngen.date.modified")}</td>
                            <td>
                              <DateShowField value={priority?.modified} asFormControl />
                            </td>
                          </tr>
                        </Table>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Modal.Body>
            </Modal>
            <ModalConfirm
              type="delete"
              component={t("ngen.priority_one")}
              name={deleteName}
              showModal={remove}
              onHide={() => setRemove(false)}
              ifConfirm={() => handleDelete(deleteUrl)}
            />
          </tbody>
        </Table>
      </ul>
    </div>
  );
};

export default TablePriorities;
