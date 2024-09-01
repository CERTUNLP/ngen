import React, { useEffect, useState } from "react";
import { Button, Col, Form, Row } from "react-bootstrap";
import { validateAlphanumeric } from "../../../utils/validators";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import { validatePlaybookName, validateUnrequiredInput } from "../../../utils/validators/playbooks";
import { useTranslation } from "react-i18next";

const animatedComponents = makeAnimated();

const FormCreatePlaybook = (props) => {
  // props:  ifConfirm name setName taxonomy setTaxonomy allTaxonomies save
  const [taxonomiesDefaultValue, setTaxonomiesDefaultValue] = useState([]);
  const { t } = useTranslation();

  useEffect(() => {
      //selected taxonomies: value-label
      if(props.taxonomy){
        let listDefaultTaxonomies = props.allTaxonomies.filter(
          elemento => props.taxonomy.includes(elemento.value)).map(elemento => ({
          value: elemento.value,
          label: elemento.label,
        }))
        setTaxonomiesDefaultValue(listDefaultTaxonomies)
      }
    }
    , [props.allTaxonomies, props.taxonomy])

  //Multiselect
  const selectTaxonomies = (event) => {
    props.setTaxonomy(
      event.map((e) => {
        return e.value;
      })
    );
  };

  return (
    <React.Fragment>
      <Form>
        <Row>
          <Col sm={12} lg={6}>
            <Form.Group controlId="Form.Playbook.Name">
              <Form.Label>
                {t("ngen.name_one")} <b style={{ color: "red" }}>*</b>
              </Form.Label>
              <Form.Control
                type="name"
                placeholder={t("ngen.name.placeholder")}
                value={props.name}
                onChange={(e) => props.setName(e.target.value)}
                isInvalid={validateUnrequiredInput(props.name) ? !validateAlphanumeric(props.name) : false}
              />
              {!validatePlaybookName(props.name) ? <div className="invalid-feedback">{t("w.validate.character")}</div> : ""}
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Col sm={12} lg={6}>
            <Form.Group controlId="Form.Playbook.Taxonomy.Multiselect">
              <Form.Label>
                {t("ngen.taxonomy_other")} <b style={{ color: "red" }}>*</b>
              </Form.Label>
              <Select
                value={taxonomiesDefaultValue}
                placeholder={t("ngen.taxonomy.other.select")}
                closeMenuOnSelect={false}
                components={animatedComponents}
                isMulti
                onChange={selectTaxonomies}
                options={props.allTaxonomies}
                className={"invalid-select"}
              />
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Group>
              {props.name !== "" && validatePlaybookName(props.name) && props.taxonomy.length > 0 ? ( //
                <>
                  <Button variant="primary" onClick={props.ifConfirm}>
                    {props.save}
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="primary" disabled>
                    {props.save}
                  </Button>
                </>
              )}
            </Form.Group>
          </Col>
        </Row>
      </Form>
    </React.Fragment>
  );
};

export default FormCreatePlaybook;
