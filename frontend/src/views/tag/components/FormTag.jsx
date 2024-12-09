import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { postTag, patchTag } from "api/services/tags";

const FormTag = (props) => {
  const [validName, setValidName] = useState("");
  const [validColor, setValidColor] = useState("");
  const { t } = useTranslation();

  const createTag = () => {
    if (props.isUpdate) {
      patchTag(props.url, props.value, props.color, true)
        .then((response) => {
          props.ifConfirm(response.data);
        })
        .catch((error) => {
          if (error.response && error.response.status == 400) {
            for (const key in error.response.data) {
              if (key === "name") {
                setValidName(error.response.data[key]);
              } else if (key === "color") {
                setValidColor(error.response.data[key]);
              }
            }
          }
        });
      return;
    }

    postTag(props.value, props.color, true)
      .then((response) => {
        props.ifConfirm(response.data);
      })
      .catch((error) => {
        if (error.response && error.response.status == 400) {
          for (const key in error.response.data) {
            if (key === "name") {
              setValidName(error.response.data[key]);
            } else if (key === "color") {
              setValidColor(error.response.data[key]);
            }
          }
        }
      });
  };

  const handleSubmit = (event) => {
    event.preventDefault(); // Prevenir el comportamiento por defecto del formulario
    createTag(); // Llamar a la función para crear/actualizar el tag
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group controlId="exampleForm.ControlInput1">
        <Form.Label>{t("ngen.value")}</Form.Label>
        <Form.Control
          type="text"
          placeholder={t("ngen.value")}
          value={props.value}
          disabled={props.isUpdate}
          onChange={(e) => {
            setValidName("");
            props.setValue(e.target.value);
          }}
          isInvalid={!!validName}
        />
        <Form.Control.Feedback type="invalid">{validName}</Form.Control.Feedback>
      </Form.Group>

      <Form.Group controlId="exampleForm.ControlSelect1">
        <Form.Label>{t("ngen.color")}</Form.Label>
        <Form.Control
          type="color"
          defaultValue="#563d7c"
          title="Choose your color"
          htmlSize="1300"
          value={props.color}
          onChange={(e) => {
            props.setColor(e.target.value);
          }}
        />
        <Form.Control.Feedback type="invalid">{validColor}</Form.Control.Feedback>
      </Form.Group>

      <div className="button-container mt-3">
        {props.color !== "" && props.value !== "" ? (
          <Button variant="primary" type="submit">
            {t("button.save")}
          </Button>
        ) : (
          <Button variant="primary" disabled>
            {t("button.save")}
          </Button>
        )}

        <Button variant="secondary" onClick={props.ifCancel} className="ml-2">
          {t("button.cancel")}
        </Button>
      </div>
    </Form>
  );
};

export default FormTag;
