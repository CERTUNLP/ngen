import React, { useEffect, useRef, useState } from "react";
import { Button, Col, Form, Row } from "react-bootstrap";
import SelectComponent from "../../../components/Select/SelectComponent";
import { useTranslation } from "react-i18next";

const FormReport = ({ body, setBody, taxonomies, createOrEdit }) => {
  const [selectTaxonomy, setSelectTaxonomy] = useState();
  const [selectLanguage, setSelectLanguage] = useState();
  const { t } = useTranslation();

  const textareaRefs = {
    problem: useRef(null),
    derived_problem: useRef(null),
    verification: useRef(null),
    recommendations: useRef(null),
    more_information: useRef(null)
  };

  const [maxHeights, setMaxHeights] = useState({
    problem: "auto",
    derived_problem: "auto",
    verification: "auto",
    recommendations: "auto",
    more_information: "auto"
  });

  const completeField = (event) => {
    setBody({
      ...body,
      [event.target.name]: event.target.value
    });
  };
  // Función para actualizar la altura máxima del div visualizador
  const updateMaxHeight = (key) => {
    if (textareaRefs[key].current) {
      const textareaHeight = textareaRefs[key].current.clientHeight;

      setMaxHeights((prevState) => ({
        ...prevState,
        [key]: textareaHeight + "px"
      }));
    }
  };

  // Manejar el cambio de tamaño de cada textarea
  useEffect(() => {
    Object.keys(textareaRefs).forEach((key) => {
      updateMaxHeight(key);
      window.addEventListener("resize", () => updateMaxHeight(key)); // Escuchar al evento resize para cada textarea
    });

    return () => {
      Object.keys(textareaRefs).forEach((key) => {
        window.removeEventListener("resize", () => updateMaxHeight(key)); // Limpiar el event listener al desmontar el componente
      });
    };
  }, []); // Ejecutar una sola vez al montar el componente

  useEffect(() => {
    if (languageOptions.length > 0) {
      languageOptions.forEach((item) => {
        if (item.value === body.lang) {
          setSelectLanguage({ label: item.label, value: item.value });
        }
      });
    }
    if (taxonomies.length > 0) {
      taxonomies.forEach((item) => {
        if (item.value === body.taxonomy) {
          setSelectTaxonomy({ label: item.label, value: item.value });
        }
      });
    }
  }, [taxonomies]);
  const completeField1 = (nameField, event, setOption) => {
    if (event) {
      setBody({
        ...body,
        [nameField]: event.value
      });
    } else {
      setBody({
        ...body,
        [nameField]: ""
      });
    }
    setOption(event);
  };
  let languageOptions = [
    {
      value: "en",
      label: t("w.language.english")
    },
    {
      value: "es",
      label: t("w.language.spanish")
    }
  ];

  return (
    <Form>
      <Row>
        <Col sm={12} lg={6}>
          <SelectComponent
            controlId="exampleForm.ControlSelect1"
            label={t("ngen.taxonomy_one")}
            options={taxonomies}
            value={selectTaxonomy}
            nameField="taxonomy"
            onChange={completeField1}
            placeholder={t("ngen.taxonomy.one.select")}
            setOption={setSelectTaxonomy}
            required={true}
          />
        </Col>
        <Col sm={12} lg={6}>
          <SelectComponent
            controlId="exampleForm.ControlSelect1"
            label={t("w.lang")}
            options={languageOptions}
            value={selectLanguage}
            nameField="lang"
            onChange={completeField1}
            placeholder={t("w.lang.select")}
            setOption={setSelectLanguage}
            required={true}
          />
        </Col>
        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>
              {t("w.issue")} <b style={{ color: "red" }}>*</b>
            </Form.Label>
            <Form.Control
              as="textarea"
              name="problem"
              value={body.problem ? body.problem : ""}
              placeholder={t("w.issue.placeholder")}
              onChange={(e) => completeField(e)}
              ref={textareaRefs.problem}
              onInput={() => updateMaxHeight("problem")}
            />
            <span style={{ color: "gray", fontSize: "0.8em" }}>{t("w.text.as.html")}</span>
          </Form.Group>
        </Col>
        <Col sm={12} lg={6}>
          <Form.Label>{t("w.preview.issue")}</Form.Label>
          <div
            style={{
              backgroundColor: "white",
              color: "black",
              maxHeight: maxHeights.problem, // Altura máxima igual a la altura actual del textarea
              overflowY: "auto",
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              marginBottom: "20px"
            }}
            dangerouslySetInnerHTML={{ __html: body.problem }}
          />
        </Col>

        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>{t("w.problem.derived")}</Form.Label>
            <Form.Control
              as="textarea"
              name="derived_problem"
              value={body.derived_problem ? body.derived_problem : ""}
              placeholder={t("w.problem.derived.placeholder")}
              onChange={(e) => completeField(e)}
              ref={textareaRefs.derived_problem}
              onInput={() => updateMaxHeight("derived_problem")}
            />
            <span style={{ color: "gray", fontSize: "0.8em" }}>{t("w.text.as.html")}</span>
          </Form.Group>
        </Col>
        <Col sm={12} lg={6}>
          <Form.Label>{t("derived.issue.preview")}</Form.Label>
          <div
            style={{
              backgroundColor: "white",
              color: "black",
              maxHeight: maxHeights.derived_problem, // Altura máxima igual a la altura actual del textarea
              // maxHeight: "200px",
              overflowY: "auto",
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              marginBottom: "20px"
            }}
            dangerouslySetInnerHTML={{ __html: body.derived_problem }}
          />
        </Col>

        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>{t("w.verification")}</Form.Label>
            <Form.Control
              as="textarea"
              name="verification"
              value={body.verification ? body.verification : ""}
              placeholder={t("w.verification.placeholder")}
              onChange={(e) => completeField(e)}
              ref={textareaRefs.verification}
              onInput={() => updateMaxHeight("verification")}
            />
            <span style={{ color: "gray", fontSize: "0.8em" }}>{t("w.text.as.html")}</span>
          </Form.Group>
        </Col>
        <Col sm={12} lg={6}>
          <Form.Label>{t("w.verification.preview")}</Form.Label>
          <div
            style={{
              backgroundColor: "white",
              color: "black",
              maxHeight: maxHeights.verification, // Altura máxima igual a la altura actual del textarea
              // maxHeight: "200px",
              overflowY: "auto",
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              marginBottom: "20px"
            }}
            dangerouslySetInnerHTML={{ __html: body.verification }}
          />
        </Col>

        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>{t("w.recommendation.other")}</Form.Label>
            <Form.Control
              as="textarea"
              name="recommendations"
              value={body.recommendations ? body.recommendations : ""}
              placeholder={t("w.recommendation.placeholder")}
              onChange={(e) => completeField(e)}
              ref={textareaRefs.recommendations}
              onInput={() => updateMaxHeight("recommendations")}
            />
            <span style={{ color: "gray", fontSize: "0.8em" }}>{t("w.text.as.html")}</span>
          </Form.Group>
        </Col>
        <Col sm={12} lg={6}>
          <Form.Label>{t("w.recommendation.preview")}</Form.Label>
          <div
            style={{
              backgroundColor: "white",
              color: "black",
              maxHeight: maxHeights.recommendations, // Altura máxima igual a la altura actual del textarea
              // maxHeight: "200px",
              overflowY: "auto",
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              marginBottom: "20px"
            }}
            dangerouslySetInnerHTML={{ __html: body.recommendations }}
          />
        </Col>

        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>{t("w.info")}</Form.Label>
            <Form.Control
              as="textarea"
              name="more_information"
              value={body.more_information ? body.more_information : ""}
              placeholder={t("w.info.placeholder")}
              onChange={(e) => completeField(e)}
              ref={textareaRefs.more_information}
              onInput={() => updateMaxHeight("more_information")}
            />
            <span style={{ color: "gray", fontSize: "0.8em" }}>{t("w.text.as.html")}</span>
          </Form.Group>
        </Col>
        <Col sm={12} lg={6}>
          <Form.Label>{t("w.info")}</Form.Label>
          <div
            style={{
              backgroundColor: "white",
              color: "black",
              maxHeight: maxHeights.more_information, // Altura máxima igual a la altura actual del textarea
              overflowY: "auto",
              padding: "10px",
              border: "1px solid #ccc",
              borderRadius: "5px",
              marginBottom: "20px"
            }}
            dangerouslySetInnerHTML={{ __html: body.more_information }}
          />
        </Col>
      </Row>

      {body.problem !== "" && body.lang !== "" && body.taxonomy !== "-1" ? (
        <Button variant="primary" onClick={createOrEdit}>
          {t("button.save")}{" "}
        </Button>
      ) : (
        <>
          <Button variant="primary" disabled>
            {t("button.save")}
          </Button>
        </>
      )}
      <Button variant="primary" href="/reports">
        {t("button.cancel")}
      </Button>
    </Form>
  );
};

export default FormReport;
