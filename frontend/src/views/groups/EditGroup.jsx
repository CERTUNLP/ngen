import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { useParams } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import { getGroup, putGroup } from "../../api/services/groups";
import FormGroup from "./components/FormGroup";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "config/constant";

const EditGroup = () => {
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [permissions, setPermissions] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();
  const { t } = useTranslation();

  useEffect(() => {
    if (id) {
      getGroup(COMPONENT_URL.group + id + "/")
        .then((response) => {
          const g = response.data;
          setUrl(g.url);
          setName(g.name);
          setPermissions(g.permissions || []);
        })
        .catch((error) => console.log(error))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const editGroup = () => {
    putGroup(url, name, permissions)
      .then(() => {
        window.location.href = "/groups";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
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
                createGroup={editGroup}
                loading={loading}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditGroup;
