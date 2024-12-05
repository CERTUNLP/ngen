import React, { useState } from "react";
import { Button, Card, Form } from "react-bootstrap";
import FormTagSelect from "./FormTagSelect";
import { useTranslation } from "react-i18next";

const FormTag = (props) => {
  const { t } = useTranslation();
  const typeOptions = [];
  const [validTag, setValidTag] = useState(false);

  return (
    <div>
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

          <FormTagsSelect
            value={props.value}
            setValue={props.setValue}
            type={props.type}
            setValidTag={setValidTag}
            validTag={validTag}
          />

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
        </Form>
      </Card.Body>
    </div>
  );
};

export default FormTag;
