import React, { useState } from "react";
import { Button, Card, Form } from "react-bootstrap";
import FormArtifactsSelect from "./FormArtifactsSelect";
import CrudButton from "components/Button/CrudButton";
import { useTranslation } from "react-i18next";

const FormArtifact = (props) => {
  const { t } = useTranslation();
  const typeOptions = [
    { value: "0", name: t("ngen.option_select") },
    { value: "ip", name: "Ip" },
    { value: "domain", name: "Domain" },
    { value: "fqdn", name: "Fqdn" },
    { value: "url", name: "Url" },
    { value: "mail", name: "Mail" },
    { value: "hash", name: "Hash" },
    { value: "file", name: "File" },
    { value: "user-agent", name: "User-agent" },
    { value: "autonomous-system", name: "Autonomous-system" },
    { value: "other", name: "Other" }
  ];
  const [validArtifact, setValidArtifact] = useState(false);

  return (
    <Card>
      <Card.Body>
        <Form>
          <Form.Group controlId="exampleForm.ControlSelect1">
            <Form.Label>{t("ngen.type")}</Form.Label>
            <Form.Control
              name="type"
              type="choice"
              as="select"
              value={props.type}
              onChange={(e) => props.setType(e.target.value)}
              isInvalid={props.type === "-1"}
            >
              {typeOptions.map((t) => {
                return <option value={t.value}>{t.name}</option>;
              })}
            </Form.Control>
          </Form.Group>

          <FormArtifactsSelect
            value={props.value}
            setValue={props.setValue}
            type={props.type}
            setValidArtifact={setValidArtifact}
            validArtifact={validArtifact}
          />
        </Form>
      </Card.Body>
      <Card.Footer>
        {props.type !== "0" && props.value !== "" ? (
          <>
            <Button variant="primary" onClick={props.ifConfirm}>
              {t("button.save")}
            </Button>
          </>
        ) : (
          <>
            <Button variant="primary" disabled>
              {t("button.save")}
            </Button>
          </>
        )}
        <CrudButton type="cancel" />
      </Card.Footer>
    </Card>
  );
};

export default FormArtifact;
