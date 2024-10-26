import React, { useEffect, useState } from "react";
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import ActiveButton from "components/Button/ActiveButton";
import CrudButton from "components/Button/CrudButton";
import DateShowField from "components/Field/DateShowField";
import { useTranslation } from "react-i18next";

function ButtonView({ taxonomyGroup }) {
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const [created, setCreated] = useState(null);
  const [modified, setModified] = useState(null);
  const [parent, setParent] = useState(null);
  const { t } = useTranslation();

  useEffect(() => {
    setCreated(taxonomyGroup.created);
    setModified(taxonomyGroup.modified);
  }, [taxonomyGroup]);


  return (
    <>
      <CrudButton type="read" onClick={handleShow} />
      <Modal size="lg" show={show} onHide={handleClose} aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("ngen.taxonomy_one")}</Card.Title>
                      <span className="d-block m-t-5">{t("ngen.taxonomy_detail")}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <Link to="./taxonomyGroups/edit" state={taxonomyGroup}>
                        <CrudButton type="edit" />
                      </Link>
                      <CloseButton aria-label="Cerrar" onClick={handleClose} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tr>
                      <td>{t("ngen.system.id")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={taxonomyGroup.slug} />
                      </td>
                      <td></td>
                    </tr>
                    <tr>
                      <td>{t("ngen.name_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={taxonomyGroup.name} />
                      </td>
                    </tr>
                    <tr>
                      <td>{t("w.active")}</td>
                      <td>
                        <ActiveButton active={+taxonomyGroup.active} />
                      </td>
                    </tr>
                    {taxonomyGroup.description === undefined ? (
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
                            defaultValue={taxonomyGroup.description}
                          />
                        </td>
                      </tr>
                    )}
                    <tr>
                      <td>{t("ngen.date.created")}</td>
                      <td>
                        <DateShowField value={created} asFormControl />
                      </td>
                    </tr>
                    <tr>
                      <td>{t("ngen.date.modified")}</td>
                      <td>
                        <DateShowField value={modified} asFormControl />
                      </td>
                    </tr>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </>
  );
}

export default ButtonView;
