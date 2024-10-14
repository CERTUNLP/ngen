import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import DropdownState from "../../components/Dropdown/DropdownState";
import { useNavigate, useParams } from "react-router-dom";
import { validateDescription, validateName, validateUnrequiredInput } from "../../utils/validators/taxonomy";
import { useTranslation } from "react-i18next";
import { putTaxonomyGroup, getTaxonomyGroup } from "../../api/services/taxonomyGroups";
import { COMPONENT_URL } from "config/constant";
import CrudButton from "components/Button/CrudButton";

const EditTaxonomyGroup = () => {
  const navigate = useNavigate();
  const [id] = useState(useParams());
  const { t } = useTranslation();

  const [url, setUrl] = useState();
  const [name, setName] = useState();
  const [description, setDescription] = useState();
  const [needs_review, setNeeds_review] = useState();

  useEffect(() => {
    if (id.id) {
      getTaxonomyGroup(COMPONENT_URL.taxonomyGroup + id.id + "/")
        .then((response) => {
          setUrl(response.data.url);
          setName(response.data.name);
          setDescription(response.data.description);
          setNeeds_review(response.data.needs_review);
        })
        .catch((error) => console.log(error));
    }
  }, [id]);

  const editTaxonomyGroup = () => {
    putTaxonomyGroup(url, name, description, needs_review).then(() => {
      navigate("/taxonomyGroups");
    });
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
                        defaultValue={name}
                        onChange={(e) => setName(e.target.value)}
                        isInvalid={!validateName(name)}
                      />
                      {validateName(name) ? "" : <div className="invalid-feedback">{t("ngen.name.invalid")}</div>}
                    </Form.Group>
                  </Col>
                  <Col sm={12} lg={2}>
                    <Form.Group>
                      <Form.Label>{t("ngen.taxonomyGroup.needs_review")}</Form.Label>
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
                        defaultValue={description}
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
                  <CrudButton type="cancel" />
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
