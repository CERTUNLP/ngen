import React, { useState } from "react";
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import { deleteFeed, getFeed, putActivationStatus } from "../../../api/services/feeds";
import CrudButton from "../../../components/Button/CrudButton";
import ActiveButton from "../../../components/Button/ActiveButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import Alert from "../../../components/Alert/Alert";
import Ordering from "../../../components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const TableFeed = ({ feeds, loading, order, setOrder, setLoading, currentPage, setIsModify }) => {
  const [remove, setRemove] = useState(false);
  const [deleteName, setDeleteName] = useState("");
  const [id, setId] = useState("");
  const [deleteUrl, setDeleteUrl] = useState("");
  const [modalShow, setModalShow] = useState(false);
  const [feed, setFeed] = useState({});
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

  const showModalChangeState = (url, name, active) => {
    setId(url.split("/")[url.split("/").length - 2]);
    setDataState({ url: url, name: name, state: active });
    setShowState(true);
  };
  const changeState = () => {
    putActivationStatus(dataState.url, !dataState.state)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      })
      .finally(() => {
        setShowState(false);
      });
  };

  const handleShow = (name, url) => {
    setDeleteName(name);
    setDeleteUrl(url);
    setRemove(true);
  };
  const handleDelete = () => {
    deleteFeed(deleteUrl)
      .then(() => {
        window.location.href = "/feeds";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setRemove(false);
      });
  };

  const showModalFeed = (feed) => {
    getFeed(feed.url).then((response) => {
      setId(response.data.url.split("/")[response.data.url.split("/").length - 2]);
      setFeed(response.data);
    });
    setModalShow(true);
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };
  const letterSize = { fontSize: "1.1em" };

  return (
    <div>
      <Card.Body>
        <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
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
              <th style={letterSize}>{t("w.active")}</th>
              <th style={letterSize}>{t("ngen.feed.associated_events")}</th>
              <th style={letterSize}>{t("ngen.options")}</th>
            </tr>
          </thead>
          <tbody>
            {feeds.map((feed, index) => {
              const parts = feed.url.split("/");
              let itemNumber = parts[parts.length - 2];
              return (
                <tr key={index}>
                  <td>{feed.name}</td>
                  <td>
                    <ActiveButton
                      active={feed.active}
                      onClick={() => showModalChangeState(feed.url, feed.name, feed.active)}
                      permissions="change_feed"
                    />
                  </td>
                  <td>{feed.events_count}</td>
                  <td>
                    <CrudButton type="read" onClick={() => showModalFeed(feed)} />
                    <CrudButton type="edit" to={`/feeds/edit/${itemNumber}`} checkPermRoute />
                    <CrudButton type="delete" onClick={() => handleShow(feed.name, feed.url)} permissions="delete_feed" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
        <ModalConfirm
          type="delete"
          component={t("ngen.feed.information")}
          name={deleteName}
          showModal={remove}
          onHide={() => setRemove(false)}
          ifConfirm={() => handleDelete(deleteUrl)}
        />
        <ModalConfirm
          type="editState"
          component={t("ngen.feed.information")}
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
                        <Card.Title as="h5">{t("ngen.feed.information")}</Card.Title>
                        <span className="d-block m-t-5">
                          {t("ngen.feed.information")} {t("w.detail")}
                        </span>
                      </Col>
                      <Col sm={12} lg={2}>
                        <CrudButton type="edit" to={`/feeds/edit/${id}`} checkPermRoute />
                        <CloseButton aria-label={t("w.close")} onClick={() => setModalShow(false)} />
                      </Col>
                    </Row>
                  </Card.Header>
                  <Card.Body>
                    <Table responsive>
                      <tr>
                        <td>{t("ngen.system.id")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={feed.slug} />
                        </td>
                        <td></td>
                      </tr>
                      <tr>
                        <td>{t("ngen.name_one")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={feed.name} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("w.active")}</td>
                        <td>
                          <ActiveButton active={feed.active} permissions="change_feed" />
                        </td>
                      </tr>
                      {feed.description === undefined ? (
                        ""
                      ) : (
                        <tr>
                          <td>{t("ngen.description")}</td>
                          <td>
                            <Form.Control
                              style={{ resize: "none" }}
                              as="textarea"
                              rows={3}
                              plaintext
                              readOnly
                              defaultValue={feed.description}
                            />
                          </td>
                        </tr>
                      )}
                      <tr>
                        <td>{t("ngen.related.info")}</td>
                        <td>
                          <Button size="sm" variant="light" className="text-capitalize">
                            {t("ngen.incident_other")}&nbsp;
                            <Badge variant="light" bg={feed.events_count > 0 ? "light" : "secondary"} className="ml-1">
                              {feed.events_count}
                            </Badge>
                          </Button>
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={feed.created ? feed.created.slice(0, 10) + " " + feed.created.slice(11, 19) : ""}
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={feed.modified ? feed.modified.slice(0, 10) + " " + feed.modified.slice(11, 19) : ""}
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
      </Card.Body>
    </div>
  );
};

export default TableFeed;
