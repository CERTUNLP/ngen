import React, { useEffect, useState } from "react";
import { Button, Col, Form, InputGroup, Row } from "react-bootstrap";
import { FiEye, FiEyeOff } from "react-icons/fi";
import CrudButton from "../../../components/Button/CrudButton";
import { useTranslation } from "react-i18next";

const CONFIG_SCHEMAS = {
  kintun: {
    host: { required: true, sensitive: false },
    port: { required: false, sensitive: false, type: "number" },
    ssl: { required: false, sensitive: false, type: "boolean" },
    api_key: { required: false, sensitive: true },
    basic_auth_username: { required: false, sensitive: false },
    basic_auth_password: { required: false, sensitive: true },
  },
  cortex: {
    host: { required: true, sensitive: false },
    port: { required: false, sensitive: false, type: "number" },
    ssl: { required: false, sensitive: false, type: "boolean" },
    api_key: { required: true, sensitive: true },
    organization: { required: false, sensitive: false },
  },
};

const ANALYZER_TYPES = Object.keys(CONFIG_SCHEMAS);

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
  const [revealedFields, setRevealedFields] = useState({});

  const toggleReveal = (field) =>
    setRevealedFields((prev) => ({ ...prev, [field]: !prev[field] }));

  useEffect(() => {
    if (!isEdit) {
      setConfig({});
    }
  }, [analyzerType, isEdit, setConfig]);

  const schema = CONFIG_SCHEMAS[analyzerType] || {};

  const handleConfigChange = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const hasValidKintunAuth = () => {
    if (analyzerType !== "kintun") return true;
    const hasApiKey = Boolean((config.api_key || "").trim());
    const hasBasicAuth =
      Boolean((config.basic_auth_username || "").trim()) &&
      Boolean((config.basic_auth_password || "").trim());
    return hasApiKey || hasBasicAuth;
  };

  const isConfigValid = () => {
    return Object.entries(schema).every(([field, meta]) => {
      if (!meta.required) return true;
      const val = config[field];
      return val && String(val).trim() !== "";
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
            {!analyzerType && (
              <div className="invalid-feedback">{t("ngen.analyzer.type_required")}</div>
            )}
          </Form.Group>
        </Col>

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
            {!name && (
              <div className="invalid-feedback">{t("w.validateName")}</div>
            )}
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
            {Object.entries(schema).map(([field, meta]) => {
              const label = getConfigFieldLabel(field, t);

              if (meta.type === "boolean") {
                return (
                  <Col sm={12} lg={6} key={field} className="d-flex align-items-center mb-3">
                    <Form.Group>
                      <Form.Check
                        type="switch"
                        id={`config-${field}`}
                        label={label}
                        checked={config[field] !== undefined ? Boolean(config[field]) : true}
                        onChange={(e) => handleConfigChange(field, e.target.checked)}
                      />
                    </Form.Group>
                  </Col>
                );
              }

              if (meta.type === "number") {
                return (
                  <Col sm={12} lg={6} key={field}>
                    <Form.Group className="mb-3">
                      <Form.Label>{label}</Form.Label>
                      <Form.Control
                        type="number"
                        min={1}
                        max={65535}
                        placeholder={label}
                        value={config[field] || ""}
                        onChange={(e) =>
                          handleConfigChange(
                            field,
                            e.target.value === "" ? "" : Number(e.target.value)
                          )
                        }
                        isInvalid={
                          config[field] !== undefined &&
                          config[field] !== "" &&
                          (config[field] < 1 || config[field] > 65535)
                        }
                      />
                      <Form.Control.Feedback type="invalid">
                        {t("ngen.analyzer.port_invalid")}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                );
              }

              const isInvalid = meta.required && !config[field];

              return (
                <Col sm={12} lg={6} key={field}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      {label}
                      {meta.required && <b style={{ color: "red" }}> *</b>}
                    </Form.Label>
                    {meta.sensitive ? (
                      <>
                        <InputGroup>
                          <Form.Control
                            type={revealedFields[field] ? "text" : "password"}
                            placeholder={label}
                            value={config[field] || ""}
                            onChange={(e) => handleConfigChange(field, e.target.value)}
                            isInvalid={isInvalid}
                          />
                          <Button
                            variant="outline-secondary"
                            onClick={() => toggleReveal(field)}
                            tabIndex={-1}
                          >
                            {revealedFields[field] ? <FiEyeOff /> : <FiEye />}
                          </Button>
                        </InputGroup>
                        {isInvalid && (
                          <div className="invalid-feedback d-block">
                            {t("ngen.analyzer.field_required", { field: label })}
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        <Form.Control
                          type="text"
                          placeholder={label}
                          value={config[field] || ""}
                          onChange={(e) => handleConfigChange(field, e.target.value)}
                          isInvalid={isInvalid}
                        />
                        {isInvalid && (
                          <div className="invalid-feedback">
                            {t("ngen.analyzer.field_required", { field: label })}
                          </div>
                        )}
                      </>
                    )}
                  </Form.Group>
                </Col>
              );
            })}
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
        <Button variant="primary" type="submit" disabled={!canSubmit}>
          {t("button.save")}
        </Button>
        <CrudButton type="cancel" />
      </Form.Group>
    </Form>
  );
};

export default FormAnalyzer;
export { CONFIG_SCHEMAS };
