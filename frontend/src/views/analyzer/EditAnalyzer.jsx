import React, { useEffect, useState } from "react";
import { Card, Col, Row, Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { getAnalyzer, putAnalyzer } from "../../api/services/analyzer";
import FormAnalyzer from "./components/FormAnalyzer";
import { COMPONENT_URL } from "config/constant";

const EditAnalyzer = () => {
  const { id } = useParams();
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [analyzerType, setAnalyzerType] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [description, setDescription] = useState("");
  const [config, setConfig] = useState({});
  const [analyzerUrl, setAnalyzerUrl] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyzer(COMPONENT_URL.analyzer + id + "/")
      .then((response) => {
        const a = response.data;
        setName(a.name);
        setAnalyzerType(a.type);
        setEnabled(a.enabled);
        setDescription(a.description || "");
        setAnalyzerUrl(a.url);
        // The backend masks sensitive fields — show them as-is
        setConfig(a.config || {});
      })
      .catch((error) => console.error(error))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = (e) => {
    e.preventDefault();
    putAnalyzer(analyzerUrl, { name, type: analyzerType, enabled, description, config })
      .then(() => {
        window.location.href = "/analyzers";
      })
      .catch((error) => console.error(error));
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
              <Card.Title as="h5">{t("ngen.analyzer.edit")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <FormAnalyzer
                name={name}
                setName={setName}
                analyzerType={analyzerType}
                setAnalyzerType={setAnalyzerType}
                enabled={enabled}
                setEnabled={setEnabled}
                description={description}
                setDescription={setDescription}
                config={config}
                setConfig={setConfig}
                isEdit={true}
                onSubmit={handleSubmit}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditAnalyzer;