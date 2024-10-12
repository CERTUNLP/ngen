import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import DropdownState from "../../components/Dropdown/DropdownState";
import { useLocation, useNavigate } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import { validateDescription, validateName, validateUnrequiredInput } from "../../utils/validators/taxonomy";
import { useTranslation } from "react-i18next";
import { putTaxonomyGroup } from "../../api/services/taxonomyGroups";

const EditTaxonomyGroup = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const fromState = location.state;
  const [taxonomyGroup] = useState(fromState);
  const { t } = useTranslation();

  const [name, setName] = useState(taxonomyGroup.name);
  const [description, setDescription] = useState(taxonomyGroup.description);
  const [needs_review, setNeeds_review] = useState(+taxonomyGroup.needs_review);

  const [showAlert, setShowAlert] = useState(false);

  const editTaxonomyGroup = () => {
    putTaxonomyGroup(taxonomyGroup.url, name, description, needs_review)
      .then(() => {
        navigate("/taxonomyGroups");
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      });
  };

  const handleClose = () => {
    navigate("/taxonomyGroups");
  }

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.taxonomy_one")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <Form>
                <Row>
                  <Col sm={12} lg={10}>
                    <Form.Group>
                      <Form.Label>
                        {t("ngen.name_one")}
                        <b style={{ color: "red" }}>*</b>
                      </Form.Label>
                      <Form.Control
                        type="text"
                        defaultValue={taxonomyGroup.name}
                        onChange={(e) => setName(e.target.value)}
                        isInvalid={!validateName(name)}
                      />
                      {validateName(name) ? "" : <div className="invalid-feedback">{t("ngen.name.invalid")}</div>}
                    </Form.Group>
                  </Col>
                  <Col sm={12} lg={2}>
                    <Form.Group>
                      <Form.Label>{t("ngen.taxonomyGroup.needs_review")}</Form.Label>
                      <DropdownState state={taxonomyGroup.needs_review} setActive={setNeeds_review} str_true="w.yes" str_false="w.no" />
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
                        defaultValue={taxonomyGroup.description}
                        onChange={(e) => setDescription(e.target.value)}
                        isInvalid={validateUnrequiredInput(description) ? !validateDescription(description) : false}
                      />
                      {validateDescription(description) ? "" : <div className="invalid-feedback">{t("ngen.description.invalid")}</div>}
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group as={Col}>
                  {validateName(name) && name !== "" ? (
                    <Button variant="primary" onClick={editTaxonomyGroup}>
                      {t("button.save")}
                    </Button>
                  ) : (
                    <Button variant="primary" disabled>
                      {t("button.save")}
                    </Button>
                  )}
                  <Button variant="info" onClick={handleClose}>
                    {t("button.close")}
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

export default EditTaxonomyGroup;
