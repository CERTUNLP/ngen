import React, { useEffect } from "react";
import { Button, Col, Form, Row } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import { useTranslation } from "react-i18next";

// Config field schemas per analyzer type.
// Keep in sync with ngen/analyzers/registry.py CONFIG_FIELDS.
const CONFIG_SCHEMAS = {
  kintun: {
    host: { required: true, sensitive: false },
    api_key: { required: false, sensitive: true },
    basic_auth_username: { required: false, sensitive: false },
    basic_auth_password: { required: false, sensitive: true },
  },
  cortex: {
    host: { required: true, sensitive: false },
    api_key: { required: true, sensitive: true },
    organization: { required: false, sensitive: false },
  },
};

const ANALYZER_TYPES = Object.keys(CONFIG_SCHEMAS);
const SENSITIVE_PLACEHOLDER = "********";
const getConfigFieldLabel = (field, t) => {
  const key = `ngen.analyzer.config_fields.${field}`;
  const translated = t(key);
  return translated === key ? field : translated;
};

const FormAnalyzer = ({
  name,
  setName,
  analyzerType,
  setAnalyzerType,
  enabled,
  setEnabled,
  description,
  setDescription,
  config,
  setConfig,
  isEdit,
  onSubmit,
}) => {
  const { t } = useTranslation();

  // When type changes, reset config to empty (keep existing values on edit)
  useEffect(() => {
    if (!isEdit) {
      setConfig({});
    }
  }, [analyzerType]);

  const schema = CONFIG_SCHEMAS[analyzerType] || {};

  const hasValidKintunAuth = () => {
    if (analyzerType !== "kintun") return true;
    const hasApiKey = Boolean((config.api_key || "").trim());
    const hasBasicAuth = Boolean((config.basic_auth_username || "").trim()) && Boolean((config.basic_auth_password || "").trim());
    return hasApiKey || hasBasicAuth;
  };

  const handleConfigChange = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const isConfigValid = () => {
    return Object.entries(schema).every(([field, meta]) => {
      if (!meta.required) return true;
      const val = config[field];
      // On edit, a sensitive field already has "********" → it's considered set
      if (isEdit && val === SENSITIVE_PLACEHOLDER) return true;
      return val && val.trim() !== "";
    });
  };

  const isFormValid = name && analyzerType && isConfigValid();
  const isKintunAuthInvalid = analyzerType === "kintun" && !hasValidKintunAuth();
  const canSubmit = isFormValid && !isKintunAuthInvalid;

  return (
    <Form onSubmit={onSubmit}>
      <Row>
        <Col sm={12} lg={6}>
          <Form.Group className="mb-3">
            <Form.Label>
              {t("ngen.name_one")} <b style={{ color: "red" }}>*</b>
            </Form.Label>
            <Form.Control
              type="text"
              placeholder={t("ngen.name_one")}
              value={name}
              onChange={(e) => setName(e.target.value)}
              isInvalid={!name}
            />
            {!name && <div className="invalid-feedback">{t("w.validateName")}</div>}
          </Form.Group>
        </Col>

        <Col sm={12} lg={6}>
          <Form.Group className="mb-3">
            <Form.Label>
              {t("ngen.analyzer.type")} <b style={{ color: "red" }}>*</b>
            </Form.Label>
            <Form.Select
              value={analyzerType}
              onChange={(e) => setAnalyzerType(e.target.value)}
              isInvalid={!analyzerType}
            >
              <option value="">{t("ngen.analyzer.select_type")}</option>
              {ANALYZER_TYPES.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </Form.Select>
            {!analyzerType && <div className="invalid-feedback">{t("ngen.analyzer.type_required")}</div>}
          </Form.Group>
        </Col>
      </Row>

      <Row>
        <Col sm={12} lg={12}>
          <Form.Group className="mb-3">
            <Form.Label>{t("ngen.description")}</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              placeholder={t("ngen.description")}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Form.Group>
        </Col>
      </Row>

      <Row>
        <Col sm={12} lg={6}>
          <Form.Group className="mb-3">
            <Form.Check
              type="switch"
              id="analyzer-enabled"
              label={t("w.active")}
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
            />
          </Form.Group>
        </Col>
      </Row>

      {analyzerType && (
        <>
          <hr />
          <Row>
            <Col>
              <h6>{t("ngen.analyzer.config")}</h6>
            </Col>
          </Row>
          <Row>
            {Object.entries(schema).map(([field, meta]) => (
              <Col sm={12} lg={6} key={field}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    {getConfigFieldLabel(field, t)}
                    {meta.required && <b style={{ color: "red" }}> *</b>}
                  </Form.Label>
                  <Form.Control
                    type={meta.sensitive ? "password" : "text"}
                    placeholder={getConfigFieldLabel(field, t)}
                    value={config[field] || ""}
                    onChange={(e) => handleConfigChange(field, e.target.value)}
                    isInvalid={
                      meta.required &&
                      !config[field] &&
                      !(isEdit && config[field] === SENSITIVE_PLACEHOLDER)
                    }
                  />
                  {meta.required && !config[field] && (
                    <div className="invalid-feedback">
                      {t("ngen.analyzer.field_required", { field: getConfigFieldLabel(field, t) })}
                    </div>
                  )}
                </Form.Group>
              </Col>
            ))}
          </Row>
          {isKintunAuthInvalid && (
            <Row>
              <Col>
                <div className="invalid-feedback d-block">
                  {t("ngen.analyzer.kintun_auth_required")}
                </div>
              </Col>
            </Row>
          )}
        </>
      )}

      <Form.Group as={Col} className="mt-3">
        {canSubmit ? (
          <Button variant="primary" type="submit">
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
  );
};

export default FormAnalyzer;
export { CONFIG_SCHEMAS, SENSITIVE_PLACEHOLDER };
