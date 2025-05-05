import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { getAnalyzerMapping, putAnalyzerMapping } from "../../api/services/analyzerMapping";
import SelectLabel from "../../components/Select/SelectLabel";
import { useTranslation } from "react-i18next";
import CrudButton from "../../components/Button/CrudButton";
import { COMPONENT_URL } from "config/constant";

const EditAnalyzerMapping = () => {
  const { id } = useParams();
  const [mappingFrom, setMappingFrom] = useState("");
  const [mappingTo, setMappingTo] = useState("");
  const [analyzerType, setAnalyzerType] = useState("");
  const [taxonomies, setTaxonomies] = useState([]);
  const [selectedMappingFrom, setSelectedMappingFrom] = useState(null);
  const [loading, setLoading] = useState(true);
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
        console.log("Error fetching taxonomies:", error);
      });
  }, []);


  useEffect(() => {
    getAnalyzerMapping(COMPONENT_URL.analyzerMapping + id + "/")
      .then((response) => {
        setMappingFrom(response.data.mapping_from);
        setMappingTo(response.data.mapping_to);
        setAnalyzerType(response.data.analyzer_type);
        setSelectedMappingFrom({
          value: response.data.mapping_from,
          label: response.data.mapping_from_name,
        });
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
      analyzer_type: analyzerType,
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
                        value={mappingTo}
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
                        value={analyzerType}
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