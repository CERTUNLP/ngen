import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, Col, Form, Row } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import { getContact } from "api/services/contacts";
import { useTranslation } from "react-i18next";

const ViewContact = () => {
  const [contact, setContact] = useState(null);
  const { id } = useParams();
  const { t } = useTranslation();

  useEffect(() => {
    if (id) {
      getContact("contacts/" + id + "/", true)
        .then((response) => setContact(response.data))
        .catch(() => setContact(null));
    }
  }, [id]);

  if (!contact) {
    return (
      <Row className="justify-content-md-center">
        <p className="text-muted">{t("w.no_data")}</p>
      </Row>
    );
  }

  return (
    <React.Fragment>
      <Row>
        <Col>
          <h1 className="h3 mb-4 text-gray-800">{t("ngen.contact_one")}: {contact.name}</h1>
        </Col>
        <Col className="text-right" style={{ textAlign: "right" }}>
          <CrudButton type="edit" to={`/contacts/edit/${id}`} checkPermRoute />
        </Col>
      </Row>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("menu.principal")}</Card.Title>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.name_one")}</b></Col>
            <Col sm={12} lg={4} className="align-self-center">
              <Form.Control plaintext readOnly defaultValue={contact.name} />
            </Col>
            <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.contact_one")}</b></Col>
            <Col sm={12} lg={4} className="align-self-center">
              <Form.Control plaintext readOnly defaultValue={contact.username} />
            </Col>
          </Row>
          <p />
          <Row>
            <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.type")}</b></Col>
            <Col sm={12} lg={4} className="align-self-center">
              <Form.Control plaintext readOnly defaultValue={contact.type} />
            </Col>
            <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.role_one")}</b></Col>
            <Col sm={12} lg={4} className="align-self-center">
              <Form.Control plaintext readOnly defaultValue={t("ngen.role." + contact.role)} />
            </Col>
          </Row>
          <p />
          {contact.public_key && (
            <Row>
              <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.public_key")}</b></Col>
              <Col sm={12} lg={10} className="align-self-center">
                <Form.Control plaintext readOnly defaultValue={contact.public_key} style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }} />
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>
    </React.Fragment>
  );
};

export default ViewContact;
