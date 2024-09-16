import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import Navigation from "../../components/Navigation/Navigation";
import { validateDescription, validateName, validateUnrequiredInput } from "../../utils/validators/taxonomy";
import { useTranslation } from "react-i18next";
import { postTaxonomyGroup } from "../../api/services/taxonomyGroups";
import DropdownState from "../../components/Dropdown/DropdownState";

const CreateTaxonomyGroup = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [showAlert, setShowAlert] = useState(false);
  const [needs_review, setNeeds_review] = useState(false);

  const { t } = useTranslation();

  useEffect(() => {

    const handleResize = (e) => {
      e.preventDefault(); // Detiene el comportamiento predeterminado del evento de redimensionamiento
      // Tu lógica de manejo de redimensionamiento aquí (si es necesario)
    };

    // Agrega un listener de redimensionamiento cuando el componente se monta
    window.addEventListener("resize", handleResize);

    // Elimina el listener cuando el componente se desmonta
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const createTaxonomyGroup = () => {
    postTaxonomyGroup(name, description, needs_review)
      .then(() => {
        navigate("/taxonomyGroups");
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  let typeOption = [
    {
      value: "vulnerability",
      label: t("ngen.vulnerability")
    },
    {
      value: "incident",
      label: t("ngen.incident")
    },
    {
      value: "other",
      label: t("ngen.other")
    }
  ];

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="taxonomy" />
      <Row>
        <Navigation actualPosition={t("w.add") + " " + t("ngen.taxonomyGroup_one")} path="/taxonomyGroups" index={t("ngen.taxonomyGroup_other")} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.taxonomyGroup_one")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <Form>
                <Row>
                  <Col sm={12} lg={10}>
                    <Form.Group>
                      <Form.Label>
                        {t("ngen.name_one")} <b style={{ color: "red" }}>*</b>
                      </Form.Label>
                      <Form.Control
                        type="text"
                        placeholder={t("ngen.name_one")}
                        onChange={(e) => setName(e.target.value)}
                        isInvalid={!validateName(name)}
                      />
                      {validateName(name) ? "" : <div className="invalid-feedback">{t("ngen.name.invalid")}</div>}
                    </Form.Group>
                  </Col>
                  <Col sm={12} lg={2}>
                    <Form.Group>
                      <Form.Label>{t("ngen.taxonomy.needs_review")}</Form.Label>
                      <DropdownState state={needs_review} setActive={setNeeds_review} str_true="w.yes" str_false="w.no" />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col sm={12} lg={12}>
                    <Form.Group>
                      <Form.Label>{t("ngen.description")}</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        placeholder={t("ngen.description")}
                        onChange={(e) => setDescription(e.target.value)}
                        isInvalid={validateUnrequiredInput(description) ? !validateDescription(description) : false}
                      />
                      {validateDescription(description) ? "" : <div className="invalid-feedback">{t("w.validateDesc")}</div>}
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group as={Col}>
                  {validateName(name) && name !== "" ? (
                    <Button variant="primary" onClick={createTaxonomyGroup}>
                      {t("button.save")}
                    </Button>
                  ) : (
                    <Button variant="primary" disabled>
                      {t("button.save")}
                    </Button>
                  )}
                  <Button variant="info" href="/taxonomyGroups">
                    {t("button.cancel")}
                  </Button>
                </Form.Group>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateTaxonomyGroup;
