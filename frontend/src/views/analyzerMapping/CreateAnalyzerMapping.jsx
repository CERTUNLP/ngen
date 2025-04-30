import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { postAnalyzerMapping } from "../../api/services/analyzerMapping";
import SelectLabel from "../../components/Select/SelectLabel";
import { useTranslation } from "react-i18next";
import CrudButton from "../../components/Button/CrudButton";

const CreateAnalyzerMapping = () => {
  const [mappingFrom, setMappingFrom] = useState("");
  const [mappingTo, setMappingTo] = useState("");
  const [analyzerType, setAnalyzerType] = useState("");
  const [taxonomies, setTaxonomies] = useState([]);
  const [selectedMappingFrom, setSelectedMappingFrom] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    getMinifiedTaxonomy()
      .then((response) => {
        const listTaxonomies = response.map((taxonomy) => ({
          value: taxonomy.url,
          label: taxonomy.name,
        }));
        setTaxonomies(listTaxonomies);
      })
      .catch((error) => {
        console.error("Error fetching taxonomies:", error);
      });
  }, []);

  const createAnalyzerMapping = () => {
    let data = {
        mapping_from: mappingFrom,
        mapping_from_name: selectedMappingFrom.label,
        mapping_to: mappingTo,
        analyzer_type: analyzerType,
    };
    postAnalyzerMapping(data)
      .then(() => {
        window.location.href = "/analyzermappings";
      })
      .catch((error) => {

        console.error("Error creating analyzer mapping:", error);
        setShowAlert(true);
      });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.analyzer_mapping")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <Form>
                <Row>
                  <Col sm={12} lg={6}>
                    <SelectLabel
                      set={setMappingFrom}
                      setSelect={setSelectedMappingFrom}
                      options={taxonomies}
                      value={selectedMappingFrom}
                      placeholder={t("ngen.analyzer_mapping.mapping_from")}
                      required={true}
                    />
                  </Col>
                  <Col sm={12} lg={6}>
                    <Form.Group>
                      <Form.Label>
                        {t("ngen.analyzer_mapping.mapping_to")} <b style={{ color: "red" }}>*</b>
                      </Form.Label>
                      <Form.Control
                        type="text"
                        placeholder={t("ngen.analyzer_mapping.mapping_to")}
                        onChange={(e) => setMappingTo(e.target.value)}
                        isInvalid={mappingTo === ""}
                      />
                      {mappingTo === "" && (
                        <div className="invalid-feedback">{t("ngen.analyzer_mapping.mapping_to") + " invalid"}</div>
                      )}
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col sm={12} lg={6}>
                    <Form.Group>
                      <Form.Label>
                        {t("ngen.analyzer_mapping.analyzer_type")} <b style={{ color: "red" }}>*</b>
                      </Form.Label>
                      <Form.Control
                        type="text"
                        placeholder={t("ngen.analyzer_mapping.analyzer_type")}
                        onChange={(e) => setAnalyzerType(e.target.value)}
                        isInvalid={analyzerType === ""}
                      />
                      {analyzerType === "" && (
                        <div className="invalid-feedback">{t("ngen.analyzer_mapping.analyzer_type") + " invalid"}</div>
                      )}
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group as={Col}>
                  {mappingFrom && mappingTo && analyzerType ? (
                    <Button variant="primary" onClick={createAnalyzerMapping}>
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

export default CreateAnalyzerMapping;