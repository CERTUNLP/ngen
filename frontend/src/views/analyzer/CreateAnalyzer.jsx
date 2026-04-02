import React, { useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { postAnalyzer } from "../../api/services/analyzer";
import FormAnalyzer from "./components/FormAnalyzer";

const CreateAnalyzer = () => {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [analyzerType, setAnalyzerType] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [description, setDescription] = useState("");
  const [config, setConfig] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    postAnalyzer({ name, type: analyzerType, enabled, description, config })
      .then(() => {
        window.location.href = "/analyzers";
      })
      .catch((error) => console.error(error));
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.analyzer.create")}</Card.Title>
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
                isEdit={false}
                onSubmit={handleSubmit}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateAnalyzer;
