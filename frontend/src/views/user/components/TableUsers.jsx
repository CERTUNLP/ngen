import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import { deleteUser, isActive } from "../../../api/services/users";
import CrudButton from "../../../components/Button/CrudButton";
import ActiveButton from "../../../components/Button/ActiveButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import Alert from "../../../components/Alert/Alert";
import Ordering from "../../../components/Ordering/Ordering";
import FormGetName from "../../../components/Form/FormGetName";
import { getGroup } from "../../../api/services/groups";
import { getPermission } from "../../../api/services/permissions";
import { getPriority } from "../../../api/services/priorities";
import { useTranslation } from "react-i18next";

function TableUsers({ users, loading, order, setOrder, setLoading, currentPage }) {
  const [remove, setRemove] = useState(false);
  const [deleteUsername, setDeleteUsername] = useState("");
  const [deleteUrl, setDeleteUrl] = useState("");
  const [modalShow, setModalShow] = useState(false);
  const [user, setUser] = useState({});
  const [showState, setShowState] = useState(false);
  const [dataState, setDataState] = useState({});
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleDelete = () => {
    deleteUser(deleteUrl)
      .then(() => {
        window.location.href = "/users";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setRemove(false);
      });
  };

  const handleShow = (username, url) => {
    setDeleteUsername(username);
    setDeleteUrl(url);
    setRemove(true);
  };

  const showModalUser = (user) => {
    setUser(user);
    setModalShow(true);
  };

  const showModalChangeState = (url, username, active) => {
    setDataState({ url: url, username: username, state: active });
    setShowState(true);
  };
  const changeState = () => {
    isActive(dataState.url, !dataState.state)
      .then(() => {
        window.location.href = "/users";
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      })
      .finally(() => {
        setShowState(false);
      });
  };
  const resetShowAlert = () => {
    setShowAlert(false);
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
                field="username"
                label={t("ngen.user.username")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <Ordering
                field="email"
                label={t("w.email")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
              <th style={letterSize}>{t("ngen.name_one")}</th>
              <th style={letterSize}>{t("ngen.state_one")}</th>
              <th style={letterSize}>{t("session.last")}</th>
              <th style={letterSize}>{t("ngen.options")}</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, index) => {
              return (
                <tr key={index}>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>{user.first_name}</td>
                  <td>
                    <ActiveButton active={user.is_active} onClick={() => showModalChangeState(user.url, user.username, user.is_active)} />
                  </td>
                  <td>{user.last_login ? user.last_login.slice(0, 10) + " " + user.last_login.slice(11, 19) : "No inicio sesion"}</td>
                  <td>
                    <CrudButton type="read" onClick={() => showModalUser(user)} />
                    <Link to="/users/edit" state={user}>
                      <CrudButton type="edit" />
                    </Link>
                    <CrudButton type="delete" onClick={() => handleShow(user.username, user.url)} />
                  </td>
                </tr>
              );
            })}
            <ModalConfirm
              type="delete"
              component={t("ngen.user")}
              name={deleteUsername}
              showModal={remove}
              onHide={() => setRemove(false)}
              ifConfirm={() => handleDelete(deleteUrl)}
            />
            <ModalConfirm
              type="editState"
              component={t("ngen.user")}
              name={dataState.username}
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
                            <Card.Title as="h5">{t("ngen.user")}</Card.Title>
                            <span className="d-block m-t-5">{t("ngen.user.detail")}</span>
                          </Col>
                          <Col sm={12} lg={4}>
                            <Link to="/users/edit" state={user}>
                              <CrudButton type="edit" />
                            </Link>
                            <CloseButton aria-label={t("w.close")} onClick={() => setModalShow(false)} />
                          </Col>
                        </Row>
                      </Card.Header>
                      <Card.Body>
                        <Table responsive>
                          <tbody>
                            {user.username !== undefined ? (
                              <tr>
                                <td>{t("ngen.user.username")}</td>
                                <td>
                                  <Form.Control plaintext readOnly defaultValue={user.username} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.email !== undefined ? (
                              <tr>
                                <td>{t("w.email")}</td>
                                <td>
                                  <Form.Control plaintext readOnly defaultValue={user.email} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.first_name !== undefined ? (
                              <tr>
                                <td>{t("ngen.name_one")}</td>
                                <td>
                                  <Form.Control plaintext readOnly defaultValue={user.first_name} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.last_name !== undefined ? (
                              <tr>
                                <td>{t("ngen.last.name")}</td>
                                <td>
                                  <Form.Control plaintext readOnly defaultValue={user.last_name} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.is_active !== undefined ? (
                              <tr>
                                <td>{t("w.active")}</td>
                                <td>
                                  <ActiveButton active={user.is_active} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.is_superuser !== undefined ? (
                              <tr>
                                <td> {t("ngen.user.is.superuser")}</td>
                                <td>
                                  <ActiveButton active={user.is_superuser} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.is_staff !== undefined ? (
                              <tr>
                                <td> {t("ngen.user.is.staff")}</td>
                                <td>
                                  <ActiveButton active={user.is_staff} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.date_joined !== undefined ? (
                              <tr>
                                <td>{t("date.creation")}</td>
                                <td>
                                  <Form.Control
                                    plaintext
                                    readOnly
                                    defaultValue={user.date_joined.slice(0, 10) + " " + user.date_joined.slice(11, 19)}
                                  />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.last_login !== undefined ? (
                              <tr>
                                <td>{t("session.last")}</td>
                                <td>
                                  <Form.Control
                                    plaintext
                                    readOnly
                                    defaultValue={user.last_login.slice(0, 10) + " " + user.last_login.slice(11, 19)}
                                  />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            <tr>
                              <td>{t("info.related")}</td>
                              <td>
                                <Button size="sm" variant="light" className="text-capitalize">
                                  Casos asignados <Badge variant="light" className="ml-1"></Badge>
                                </Button>
                              </td>
                            </tr>
                            {user.priority !== undefined ? (
                              <tr>
                                <td>{t("ngen.priority_one")}</td>
                                <td>
                                  <FormGetName form={true} get={getPriority} url={user.priority} key={1} />
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}

                            {user.groups !== undefined && user.groups.length >= 0 ? (
                              <tr>
                                <td>{t("w.groups")}</td>
                                <td>
                                  {Object.values(user.groups).map((groupItem, index) => {
                                    return <FormGetName form={true} get={getGroup} url={groupItem} key={index} />;
                                  })}
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
                            {user.user_permissions !== undefined && user.user_permissions.length >= 0 ? (
                              <tr>
                                <td>{t("w.permissions")}</td>
                                <td>
                                  {Object.values(user.user_permissions).map((permissionItem, index) => {
                                    return <FormGetName form={true} get={getPermission} url={permissionItem} key={index} />;
                                  })}
                                </td>
                              </tr>
                            ) : (
                              <></>
                            )}
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
}

export default TableUsers;
