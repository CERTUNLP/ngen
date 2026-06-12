import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, Col, Form, Row, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import { getNetwork } from "api/services/networks";
import { getContact } from "api/services/contacts";
import PermissionCheck from "components/Auth/PermissionCheck";
import { useTranslation } from "react-i18next";

const ViewNetwork = () => {
  const [network, setNetwork] = useState(null);
  const [contacts, setContacts] = useState([]);
  const { id } = useParams();
  const { t } = useTranslation();

  useEffect(() => {
    if (id) {
      getNetwork("networks/" + id + "/", true)
        .then((response) => {
          const netData = response.data;
          setNetwork(netData);
          if (netData.contacts?.length > 0) {
            Promise.all(netData.contacts.map((url) => getContact(url, true)))
              .then((responses) => setContacts(responses.map((r) => r.data)))
              .catch(() => setContacts([]));
          }
        })
        .catch(() => setNetwork(null));
    }
  }, [id]);

  if (!network) {
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
          <h1 className="h3 mb-4 text-gray-800">{t("ngen.network_one")}: {network.cidr || network.domain}</h1>
        </Col>
        <Col className="text-right" style={{ textAlign: "right" }}>
          <CrudButton type="edit" to={`/networks/edit/${id}`} checkPermRoute />
        </Col>
      </Row>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("menu.principal")}</Card.Title>
        </Card.Header>
        <Card.Body>
          {network.cidr && (
            <>
              <Row>
                <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.cidr")}</b></Col>
                <Col sm={12} lg={4} className="align-self-center">
                  <Form.Control plaintext readOnly defaultValue={network.cidr} />
                </Col>
              </Row>
              <p />
            </>
          )}
          {network.domain && (
            <>
              <Row>
                <Col sm={12} lg={2} className="align-self-center"><b>{t("ngen.domain")}</b></Col>
                <Col sm={12} lg={4} className="align-self-center">
                  <Form.Control plaintext readOnly defaultValue={network.domain} />
                </Col>
              </Row>
              <p />
            </>
          )}
          <Row>
            <Col sm={12} lg={2} className="align-self-center"><b>{t("w.active")}</b></Col>
            <Col sm={12} lg={4} className="align-self-center">
              <Form.Control plaintext readOnly defaultValue={network.active ? t("w.yes") : t("w.no")} />
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <PermissionCheck permissions={["view_contact"]}>
        {contacts.length > 0 && (
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.contact_other")} ({contacts.length})</Card.Title>
            </Card.Header>
            <Card.Body>
              <Table responsive hover size="sm">
                <thead>
                  <tr>
                    <th>{t("ngen.name_one")}</th>
                    <th>{t("ngen.contact_one")}</th>
                    <th>{t("ngen.type")}</th>
                    <th>{t("ngen.role_one")}</th>
                  </tr>
                </thead>
                <tbody>
                  {contacts.map((c, index) => (
                    <tr key={index}>
                      <td><Form.Control plaintext readOnly defaultValue={c.name} /></td>
                      <td><Form.Control plaintext readOnly defaultValue={c.username} /></td>
                      <td><Form.Control plaintext readOnly defaultValue={c.type} /></td>
                      <td><Form.Control plaintext readOnly defaultValue={t("ngen.role." + c.role)} /></td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        )}
      </PermissionCheck>
    </React.Fragment>
  );
};

export default ViewNetwork;
