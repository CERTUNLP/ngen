import React, { useState } from "react";
import { Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import { Link } from "react-router-dom";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import { deleteTaxonomyGroup, getTaxonomyGroup } from "../../../api/services/taxonomyGroups";
import Ordering from "../../../components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const TableTaxonomyGroup = ({ setIsModify, list, loading, order, setOrder, setLoading }) => {
  const [modalDelete, setModalDelete] = useState(false);
  const [url, setUrl] = useState(null);
  const [name, setName] = useState(null);
  const [taxonomyGroup, setTaxonomyGroup] = useState();
  const [modalShow, setModalShow] = useState(false);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleClose = () => setModalShow(false);

  const Delete = (url, name) => {
    setUrl(url);
    setName(name);
    setModalDelete(true);
  };

  const showTaxonomyGroup = (url) => {
    getTaxonomyGroup(url)
      .then((response) => {
        setTaxonomyGroup(response.data);
        setModalShow(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const removeTaxonomyGroup = (url, name) => {
    deleteTaxonomyGroup(url, name)
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

  const letterSize = { fontSize: "1.1em" };
  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <Ordering
              field="created"
              label={t("date.creation")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="name"
              label={t("ngen.name_one")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="description"
              label={t("ngen.description")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="needs_review"
              label={t("ngen.taxonomyGroup.needs_review")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <th style={letterSize}>{t("ngen.options")}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((taxonomyGroup, index) => (
            <tr key={index}>
              <td>{taxonomyGroup.created.slice(0, 10) + " " + taxonomyGroup.created.slice(11, 19)}</td>
              <td>{taxonomyGroup.name}</td>
              <td>{taxonomyGroup.description}</td>
              <td>{taxonomyGroup.needs_review ? t("w.yes") : t("w.no")}</td>
              <td>
                <CrudButton type="read" onClick={() => showTaxonomyGroup(taxonomyGroup.url)} />
                <Link to="/taxonomyGroups/edit" state={taxonomyGroup}>
                  <CrudButton type="edit" />
                </Link>
                <CrudButton type="delete" onClick={() => Delete(taxonomyGroup.url, taxonomyGroup.name)} />
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <Modal size="lg" show={modalShow} onHide={handleClose} aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("ngen.taxonomyGroup_one")}</Card.Title>
                      <span className="d-block m-t-5">{t("ngen.taxonomyGroup.detail")}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <Link to="/taxonomyGroups/edit" state={taxonomyGroup}>
                        <CrudButton type="edit" />
                      </Link>
                      <CloseButton aria-label={t("w.close")} onClick={handleClose} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      <tr>
                        <td>{t("ngen.system.id")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomyGroup ? taxonomyGroup.slug : ""} />
                        </td>
                        <td></td>
                      </tr>
                      <tr>
                        <td>{t("ngen.name_one")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomyGroup ? taxonomyGroup.name : ""} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.taxonomyGroup.needs_review")}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={taxonomyGroup ? (taxonomyGroup.needs_review ? t("w.yes") : t("w.no")) : ""}
                          />
                        </td>
                      </tr>
                      {taxonomyGroup && Boolean(taxonomyGroup.description) && (
                        <tr>
                          <td>{t("ngen.description")}</td>
                          <td>
                            <Form.Control
                              style={{ resize: "none" }}
                              as="textarea"
                              rows={3}
                              plaintext
                              readOnly
                              defaultValue={taxonomyGroup.description}
                            />
                          </td>
                        </tr>
                      )}
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={taxonomyGroup ? taxonomyGroup.created.slice(0, 10) + " " + taxonomyGroup.created.slice(11, 19) : ""}
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={taxonomyGroup ? taxonomyGroup.modified.slice(0, 10) + " " + taxonomyGroup.modified.slice(11, 19) : ""}
                          />
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
        component={t("ngen.taxonomyGroup_one")}
        name={name}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeTaxonomyGroup(url, name)}
      />
    </React.Fragment>
  );
};

export default TableTaxonomyGroup;
