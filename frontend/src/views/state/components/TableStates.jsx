import React, { useState } from "react";
import { Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import ActiveButton from "components/Button/ActiveButton";
import ModalConfirm from "components/Modal/ModalConfirm";
import { deleteState, getState, isActive } from "api/services/states";
import Alert from "components/Alert/Alert";
import CallBackendByName from "components/CallBackendByName";
import DateShowField from "components/Field/DateShowField";
import { useTranslation } from "react-i18next";

const TableStates = ({ states, callback, loading, currentPage, setIsModify }) => {
  const [deleteName, setDeleteName] = useState();
  const [deleteUrl, setDeleteUrl] = useState();
  const [id, setId] = useState("");
  const [remove, setRemove] = useState();
  const [dataState, setDataState] = useState({});
  const [showState, setShowState] = useState();
  const [state, setState] = useState({});
  const [modalShow, setModalShow] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const modalDelete = (name, url) => {
    setDeleteName(name);
    setDeleteUrl(url);
    setRemove(true);
  };
  const handleDelete = () => {
    deleteState(deleteUrl, deleteName)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setRemove(false);
      });
  };
  const modalChangeState = (url, name, active) => {
    setDataState({ url: url, name: name, state: active });
    setShowState(true);
  };
  const callbackState = (url, setPriority) => {
    getState(url)
      .then((response) => {
        setPriority(response.data);
      })
      .catch();
  };
  const changeState = () => {
    isActive(dataState.url, +!dataState.state)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setShowState(false);
      });
  };
  const showModalState = (state) => {
    setId(state.url.split("/")[state.url.split("/").length - 2]);
    setState(state);
    setModalShow(true);
  };
  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />

      <ul className="list-group my-4">
        <Table responsive hover className="text-center">
          <thead>
            <tr>
              <th>{t("ngen.name_one")}</th>
              <th>{t("ngen.state_one")}</th>
              <th>{t("w.attended")}</th>
              <th>{t("w.solved")}</th>
              <th>{t("ngen.options")}</th>
            </tr>
          </thead>
          <tbody>
            {states.map((state, index) => {
              const parts = state.url.split("/");
              let itemNumber = parts[parts.length - 2];
              return (
                <tr key={index}>
                  <td>{state.name}</td>
                  <td>
                    <ActiveButton
                      active={state.active}
                      onClick={() => modalChangeState(state.url, state.name, state.active)}
                      permissions="change_state"
                    />
                  </td>
                  <td>{state.attended ? t("ngen.true") : t("ngen.false")}</td>

                  <td>{state.solved ? t("ngen.true") : t("ngen.false")}</td>

                  <td>
                    <CrudButton type="read" onClick={() => showModalState(state)} />
                    <CrudButton type="edit" to={`/states/edit/${itemNumber}`} checkPermRoute />
                    <CrudButton type="delete" onClick={() => modalDelete(state.name, state.url)} permissions="delete_state" />
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
              name={dataState.name}
              state={dataState.state}
              showModal={showState}
              onHide={() => setShowState(false)}
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
                            <Card.Title as="h5">{t("ngen.state_one")}</Card.Title>
                            <span className="d-block m-t-5">{t("ngen.state.detail")}</span>
                          </Col>
                          <Col sm={12} lg={4}>
                            <CrudButton type="edit" to={`/states/edit/${id}`} checkPermRoute />
                            <CloseButton aria-label={t("w.close")} onClick={() => setModalShow(false)} />
                          </Col>
                        </Row>
                      </Card.Header>
                      <Card.Body>
                        <Table responsive>
                          <tbody>
                            <tr>
                              <td>{t("ngen.name_one")}</td>
                              <td>
                                <Form.Control plaintext readOnly defaultValue={state.name} />
                              </td>
                              <td></td>
                            </tr>
                            <tr>
                              <td>{t("w.attended")}</td>
                              <td>
                                <Form.Control plaintext readOnly defaultValue={state.attended} />
                              </td>
                            </tr>
                            <tr>
                              <td>{t("w.solved")}</td>
                              <td>
                                <Form.Control plaintext readOnly defaultValue={state.solved} />
                              </td>
                            </tr>

                            <tr>
                              <td>{t("w.active")}</td>
                              <td>
                                <ActiveButton active={state.active} />
                              </td>
                            </tr>
                            <tr>
                              <td>{t("ngen.description")}</td>
                              <td>
                                <Form.Control plaintext readOnly defaultValue={state.description} />
                              </td>
                            </tr>
                            <tr>
                              <td>{t("ngen.children")}</td>
                              <td>
                                {state.children
                                  ? state.children.map((url) => {
                                      return <CallBackendByName url={url} callback={callbackState} useBadge={false} />;
                                    })
                                  : "No tiene hijos"}
                              </td>
                            </tr>
                            <tr>
                              <td>{t("ngen.date.created")}</td>
                              <td>
                                <DateShowField value={state?.created} asFormControl />
                              </td>
                            </tr>
                            <tr>
                              <td>{t("ngen.date.modified")}</td>
                              <td>
                                <DateShowField value={state?.modified} asFormControl />
                              </td>
                            </tr>
                          </tbody>
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
    </div>
  );
};

export default TableStates;
