import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { getMinifiedAnalyzer, getVulnChoices } from "../../api/services/analyzer";
import { getAnalyzerMapping, putAnalyzerMapping } from "../../api/services/analyzerMapping";
import SelectLabel from "../../components/Select/SelectLabel";
import { useTranslation } from "react-i18next";
import CrudButton from "../../components/Button/CrudButton";
import { COMPONENT_URL } from "config/constant";

const EditAnalyzerMapping = () => {
  const { id } = useParams();
  const [mappingFrom, setMappingFrom] = useState("");
  const [mappingTo, setMappingTo] = useState("");
  const [analyzer, setAnalyzer] = useState("");
  const [taxonomies, setTaxonomies] = useState([]);
  const [analyzerOptions, setAnalyzerOptions] = useState([]);
  const [selectedMappingFrom, setSelectedMappingFrom] = useState(null);
  const [selectedAnalyzer, setSelectedAnalyzer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [vulnChoices, setVulnChoices] = useState({});
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
        console.log("Error fetching taxonomies:", error);
      });

    getMinifiedAnalyzer()
      .then((analyzers) => {
        const options = analyzers
          .filter((a) => a.enabled)
          .map((a) => ({ value: a.url, label: a.name, type: a.type }));
        setAnalyzerOptions(options);
      })
      .catch((error) => {
        console.error("Error fetching analyzers:", error);
      });

    getVulnChoices()
      .then((choices) => setVulnChoices(choices))
      .catch((error) => console.error("Error fetching vuln choices:", error));
  }, []);


  useEffect(() => {
    getAnalyzerMapping(COMPONENT_URL.analyzerMapping + id + "/")
      .then((response) => {
        setMappingFrom(response.data.mapping_from);
        setMappingTo(response.data.mapping_to);
        setAnalyzer(response.data.analyzer || "");
        setSelectedMappingFrom({
          value: response.data.mapping_from,
          label: response.data.mapping_from_name,
        });
        if (response.data.analyzer) {
          setSelectedAnalyzer({
            value: response.data.analyzer,
            label: response.data.analyzer_name,
            type: response.data.analyzer_type,
          });
        }
      })
      .catch((error) => {
        console.log("Error fetching analyzer mapping:", error);
      })
      .finally(() => {
        setLoading(false);
        setShowAlert(true);
      });
  }, [id]);


  const editAnalyzerMapping = () => {
    const data = {
      mapping_from: mappingFrom,
      mapping_from_name: selectedMappingFrom.label,
      mapping_to: mappingTo,
      analyzer: analyzer || null,
    };

    putAnalyzerMapping(COMPONENT_URL.analyzerMapping + id + "/", data)
      .then(() => {
        window.location.href = "/analyzermappings";
      })
      .catch((error) => {
        console.log("Error updating analyzer mapping:", error);
        setShowAlert(true);
      });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

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
                  <Col sm={12} lg={4}>
                    <SelectLabel
                      set={setAnalyzer}
                      setSelect={setSelectedAnalyzer}
                      options={analyzerOptions}
                      value={selectedAnalyzer}
                      placeholder={t("ngen.analyzer_mapping.analyzer_type")}
                      required={true}
                    />
                  </Col>
                  <Col sm={12} lg={4}>
                    <SelectLabel
                      set={setMappingFrom}
                      setSelect={setSelectedMappingFrom}
                      options={taxonomies}
                      value={selectedMappingFrom}
                      placeholder={t("ngen.analyzer_mapping.mapping_from")}
                      required={true}
                    />
                  </Col>
                  <Col sm={12} lg={4}>
                    <Form.Group>
                      <Form.Label>
                        {t("ngen.analyzer_mapping.mapping_to")} <b style={{ color: "red" }}>*</b>
                      </Form.Label>
                      {(() => {
                        const choices = vulnChoices[selectedAnalyzer?.type] || [];
                        return choices.length > 0 ? (
                          <Form.Select
                            value={mappingTo}
                            onChange={(e) => setMappingTo(e.target.value)}
                            isInvalid={mappingTo === ""}
                          >
                            <option value="">{t("ngen.analyzer_mapping.mapping_to_select")}</option>
                            {choices.map((v) => (
                              <option key={v} value={v}>{v}</option>
                            ))}
                          </Form.Select>
                        ) : (
                          <Form.Control
                            type="text"
                            value={mappingTo}
                            onChange={(e) => setMappingTo(e.target.value)}
                            isInvalid={mappingTo === ""}
                          />
                        );
                      })()}
                      {mappingTo === "" && (
                        <div className="invalid-feedback">{t("ngen.analyzer_mapping.mapping_to") + " invalid"}</div>
                      )}
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group as={Col}>
                  {mappingFrom && mappingTo ? (
                    <Button variant="primary" onClick={editAnalyzerMapping}>
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

export default EditAnalyzerMapping;