import React, { useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { postEntity } from "../../api/services/entities";
import FormEntity from "./components/FormEntity";
import Navigation from "../../components/Navigation/Navigation";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const CreateEntity = () => {
  const [name, setName] = useState("");
  const active = true; //se crea activo por defecto

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  //Create
  const addEntity = () => {
    postEntity(name, active)
      .then((response) => {
        window.location.href = "/entities";
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      });
  };

  const { t } = useTranslation();

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="entity" />
      <Row>
        <Navigation actualPosition={t("ngen.entity_add")} path="/entities" index={t("ngen.entity_other")} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.entity_other")}</Card.Title>
              <span className="d-block m-t-5">{t("ngen.entity_add")}</span>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col sm={12} lg={12}>
                  <FormEntity name={name} setName={setName} ifConfirm={addEntity} edit={false} />
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateEntity;
