import React, { useEffect, useState } from "react";
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import ActiveButton from "components/Button/ActiveButton";
import CrudButton from "components/Button/CrudButton";
import { getTaxonomy } from "api/services/taxonomies";
import DateShowField from "components/Field/DateShowField";
import { useTranslation } from "react-i18next";

function ButtonView({ taxonomy }) {
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const [created, setCreated] = useState(null);
  const [modified, setModified] = useState(null);
  const [parent, setParent] = useState(null);
  const { t } = useTranslation();

  useEffect(() => {
    taxonomyParent();
    let datetime = taxonomy.created.split("T");
    setCreated(datetime[0] + " " + datetime[1].slice(0, 8));
    datetime = taxonomy.modified.split("T");
    setModified(datetime[0] + " " + datetime[1].slice(0, 8));
  }, [taxonomy]);

  const taxonomyParent = () => {
    getTaxonomy(taxonomy.parent)
      .then((response) => {
        setParent(response.data.name);
      })
      .catch((error) => {
        console.log(error);
      });
  };

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
                      <Link to="./taxonomy/edit" state={taxonomy}>
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
                        <Form.Control plaintext readOnly defaultValue={taxonomy.slug} />
                      </td>
                      <td></td>
                    </tr>
                    <tr>
                      <td>{t("ngen.name_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={taxonomy.name} />
                      </td>
                    </tr>
                    <tr>
                      <td>{t("w.active")}</td>
                      <td>
                        <ActiveButton active={+taxonomy.active} />
                      </td>
                    </tr>
                    <tr>
                      <td>{t("ngen.type")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={taxonomy.type} />
                      </td>
                    </tr>
                    {taxonomy.description === undefined ? (
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
                            defaultValue={taxonomy.description}
                          />
                        </td>
                      </tr>
                    )}
                    {taxonomy.parent === undefined ? (
                      ""
                    ) : (
                      <tr>
                        <td>{t("ngen.taxonomy.parent")}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={parent} />
                        </td>
                      </tr>
                    )}
                    <tr>
                      <td>{t("info.related")}</td>
                      <td>
                        <Button size="sm" variant="light" className="text-capitalize">
                          {t("ngen.report_other")}
                          <Badge variant="light" className="ml-1">
                            {taxonomy.reports.length}
                          </Badge>
                        </Button>
                      </td>
                    </tr>
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
