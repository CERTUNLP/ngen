import React, { useState } from "react";
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import ActiveButton from "../../../components/Button/ActiveButton";
import CrudButton from "../../../components/Button/CrudButton";
import { deleteEntity, getEntity, isActive } from "../../../api/services/entities";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import Ordering from "../../../components/Ordering/Ordering";
import DateShowField from "components/Field/DateShowField";
import { useTranslation } from "react-i18next";

const TableEntity = ({ setIsModify, list, loading, setLoading, currentPage, order, setOrder, basePath = "" }) => {
  const [entity, setEntity] = useState("");
  const [modalShow, setModalShow] = useState(false);
  const [modalDelete, setModalDelete] = useState(false);
  const [modalState, setModalState] = useState(false);
  const [url, setUrl] = useState("");
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [active, setActive] = useState("");
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  //Read Entity
  const showEntity = (url) => {
    setId(url.split("/")[url.split("/").length - 2]);
    setUrl(url);
    setEntity("");
    getEntity(url)
      .then((response) => {
        setEntity(response.data);
        setModalShow(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  // Remove Entity
  const Delete = (url, name) => {
    setUrl(url);
    setName(name);
    setModalDelete(true);
  };

  const removeEntity = (url, name) => {
    deleteEntity(url, name)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalDelete(false);
      });
  };

  //Update Entity
  const pressActive = (url, active, name) => {
    setUrl(url);
    setName(name);
    setActive(active);
    setModalState(true);
  };

  const switchState = (url, state, name) => {
    isActive(url, !state, name)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalState(false);
        setModalShow(false);
      });
  };

  const storageEntityUrl = (url) => {
    localStorage.setItem("entity", url);
  };

  const letterSize = { fontSize: "1.1em" };
  return (
    <React.Fragment>
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
            <th>{t("w.active")}</th>
            <th>{t("ngen.network.associated")}</th>
            <th>{t("ngen.action_one")}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((entity, index) => {
            const parts = entity.url.split("/");
            let itemNumber = parts[parts.length - 2];
            return (
              <tr key={index}>
                <td>{entity.name}</td>
                <td>
                  <ActiveButton
                    active={entity.active}
                    onClick={() => pressActive(entity.url, entity.active, entity.name)}
                    permissions="change_networkentity"
                  />
                </td>
                <td>{entity.networks.length}</td>
                <td>
                  <CrudButton type="read" onClick={() => showEntity(entity.url)} />
                  <CrudButton type="edit" to={`${basePath}/entities/edit/${itemNumber}`} checkPermRoute />
                  <CrudButton type="delete" onClick={() => Delete(entity.url, entity.name)} permissions="delete_networkentity" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>

      <Modal size="lg" show={modalShow} onHide={() => setModalShow(false)} aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("ngen.entity_other")}</Card.Title>
                      <span className="d-block m-t-5">{t("ngen.entity_detail")}</span>
                    </Col>
                    <Col sm={12} lg={3}>
                      <CrudButton type="edit" to={`${basePath}/entities/edit/${id}`} checkPermRoute />
                      <CloseButton aria-label={t("w.close")} onClick={() => setModalShow(false)} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      <tr>
                        <td>{t("ngen.system.id")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={id} />
                        </td>
                        <td></td>
                      </tr>
                      <tr>
                        <td>{t("ngen.name_one")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={entity.name} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("w.active")}</td>
                        <td>
                          <ActiveButton active={entity.active} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td>
                          <DateShowField value={entity?.created} asFormControl />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td>
                          <DateShowField value={entity?.modified} asFormControl />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.related.info")}</td>
                        <td>
                          <Button size="sm" variant="light" className="text-capitalize">
                            {t("ngen.network_other")}&nbsp;
                            <Badge variant="light" className="ml-1" bg={entity?.networks?.length > 0 ? "primary" : "secondary"}>
                              {entity?.networks?.length}
                            </Badge>
                          </Button>
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

      <ModalConfirm
        type="delete"
        component={t("ngen.entity")}
        name={name}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeEntity(url, name)}
      />

      <ModalConfirm
        type="editState"
        component={t("ngen.entity")}
        name={name}
        state={active}
        showModal={modalState}
        onHide={() => setModalState(false)}
        ifConfirm={() => switchState(url, active, name)}
      />
    </React.Fragment>
  );
};

export default TableEntity;
