import React, { useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { postGroup } from "../../api/services/groups";
import Alert from "../../components/Alert/Alert";
import FormGroup from "./components/FormGroup";
import { useTranslation } from "react-i18next";

const CreateGroup = () => {
  const [name, setName] = useState("");
  const [permissions, setPermissions] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  const createGroup = () => {
    postGroup(name, permissions)
      .then(() => {
        window.location.href = "/groups";
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      });
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("w.groups")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <FormGroup
                name={name}
                setName={setName}
                permissions={permissions}
                setPermissions={setPermissions}
                createGroup={createGroup}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateGroup;
