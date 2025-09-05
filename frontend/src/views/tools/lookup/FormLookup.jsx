import React, { useState, useEffect, useRef } from "react";
import { Button, Col, Form, Row, Spinner, Alert, Accordion, Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import CrudButton from "components/Button/CrudButton";
import { lookup, getTask } from "api/services/tools";
import { validateAddressValueOrNetworkOrDomain } from "utils/validators/network";
import ReactJson from "react18-json-view";
import "./monokai.css";

const FormLookup = () => {
  const { t } = useTranslation();

  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [taskUrl, setTaskUrl] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [taskResult, setTaskResult] = useState(null);
  const pollingRef = useRef(null);

  const handleChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTaskResult(null);
    setTaskStatus(null);

    lookup(inputValue)
      .then((response) => {
        console.log("Lookup response:", response);
        setTaskUrl(response.url); // Ej: { task_url: "/api/task/123/" }
      })
      .catch((error) => {
        console.error(error);
        setTaskStatus("FAILURE");
        setTaskResult(t("lookup.error.start"));
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // Pooleo al task service
  useEffect(() => {
    if (!taskUrl) return;
    setTaskStatus("PENDING");
    pollingRef.current = setInterval(() => {
      getTask(taskUrl)
        .then((taskData) => {
          let data = taskData.data;
          setTaskStatus(data.status);

          if (data.status === "SUCCESS") {
            setTaskResult(data.result);
            clearInterval(pollingRef.current);
          } else if (data.status === "FAILURE") {
            setTaskResult(t("lookup.error.run"));
            clearInterval(pollingRef.current);
          } else if (data.status === "PENDING") {
            // Do nothing, just keep polling
          }
        })
        .catch((error) => {
          console.error(error);
          setTaskStatus("FAILURE");
          setTaskResult(t("lookup.error.fetch"));
          clearInterval(pollingRef.current);
        });
    }, 2000);

    return () => clearInterval(pollingRef.current);
  }, [taskUrl]);
  // Función auxiliar para mostrar info completa del dominio/host
  const renderSummary = (data) => {
    try {
      const original = data?.original;
      const domain = original?.query || "-";
      const type = original?.type || "-";

      const whoisRaw = original?.data?.whois?.raw || {};
      const whoisError = original?.data?.whois?.error || null;
      const registrar = whoisRaw?.registrar || "-";
      const creation = whoisRaw?.creation_date || "-";
      const expiration = whoisRaw?.expiration_date || "-";

      const rdapRaw = original?.data?.rdap?.raw || {};
      const rdapError = original?.data?.rdap?.error || null;
      const handle = rdapRaw?.handle || "-";
      const ipVersion = rdapRaw?.ip_version || "-";
      const assignmentType = rdapRaw?.assignment_type || "-";

      // Entidades
      const entities = rdapRaw?.entities || {};
      const registrant = entities.registrant?.map((e) => e.name).join(", ") || "-";
      const administrative = entities.administrative?.map((e) => `${e.name} (${e.email || "-"})`).join(", ") || "-";
      const technical = entities.technical?.map((e) => `${e.name} (${e.email || "-"})`).join(", ") || "-";
      const abuseEntities = entities.abuse?.map((e) => `${e.name} (${e.email || "-"})`).join(", ") || "-";

      // Todos los abuse emails encontrados
      const abuseEmails = data?.abuse_emails || [];

      const securityError = original?.data?.securitytxt?.error || null;

      // --- NUEVO: datos de ngen ---
      const ngen = data?.ngen || {};
      const ngenQuery = ngen?.query || "-";
      const ngenType = ngen?.type || "-";
      const ngenNetwork = ngen?.data?.network || "-";
      const ngenEntity = ngen?.data?.entity || "-";
      const ngenAbuseEmails = ngen?.data?.abuse_emails || [];
      const ngenGlobalAbuse = ngen?.abuse_emails || [];

      return (
        <div>
          <hr />
          <h5>{t("ngen.lookup.ngen_info")}</h5>
          <p>
            <b>{t("ngen.lookup.domain")}:</b> {ngenQuery}
          </p>
          <p>
            <b>{t("ngen.lookup.type")}:</b> {ngenType}
          </p>
          <p>
            <b>{t("ngen.lookup.network")}:</b> {ngenNetwork}
          </p>
          <p>
            <b>{t("ngen.lookup.entity")}:</b> {ngenEntity}
          </p>
          <p>
            <b>{t("ngen.lookup.abuse_emails")}:</b> {ngenAbuseEmails.length > 0 ? ngenAbuseEmails.join(", ") : "-"}
          </p>

          <hr />
          <h5>{t("ngen.lookup.external_info")}</h5>
          <p>
            <b>{t("ngen.lookup.domain")}:</b> {domain}
          </p>
          <p>
            <b>{t("ngen.lookup.type")}:</b> {type}
          </p>
          <p>
            <b>{t("ngen.lookup.registrar")}:</b> {registrar}
          </p>
          <p>
            <b>{t("ngen.lookup.creation")}:</b> {creation}
          </p>
          <p>
            <b>{t("ngen.lookup.expiration")}:</b> {expiration}
          </p>
          <p>
            <b>{t("ngen.lookup.handle")}:</b> {handle}
          </p>
          <p>
            <b>{t("ngen.lookup.assignment_type")}:</b> {assignmentType}
          </p>
          <p>
            <b>{t("ngen.lookup.registrant")}:</b> {registrant}
          </p>
          <p>
            <b>{t("ngen.lookup.administrative")}:</b> {administrative}
          </p>
          <p>
            <b>{t("ngen.lookup.technical")}:</b> {technical}
          </p>
          <p>
            <b>{t("ngen.lookup.abuse_entities")}:</b> {abuseEntities}
          </p>
          <p>
            <b>{t("ngen.lookup.abuse_emails_original_query")}:</b> {data?.original?.abuse_emails?.join(", ") || "-"}
          </p>
          <p>
            <b>{t("ngen.lookup.rdap_abuse_hostname")}:</b> {data?.hostname?.abuse_emails?.join(", ") || "-"}
          </p>
          <p>
            <b>{t("ngen.lookup.security_txt_abuse_emails")}:</b> {data?.securitytxt?.abuse_emails?.join(", ") || "-"}
          </p>
          <p>
            <b>{t("ngen.lookup.abuse_emails_ip_associated_with_domain")}:</b> {data?.solved_domain?.abuse_emails?.join(", ") || "-"}
          </p>
          <p>
            <b>{t("ngen.lookup.abuse_emails_sld_domain")}:</b> {data?.sld_hostname?.abuse_emails?.join(", ") || "-"}
          </p>

          <p>
            <div>
              <b>{t("ngen.lookup.all_abuse_emails")}:</b>
              {abuseEmails.length > 0 ? (
                <ul>
                  {abuseEmails.map((email, idx) => (
                    <li key={idx}>{email}</li>
                  ))}
                </ul>
              ) : (
                <span> - </span>
              )}
            </div>
          </p>

          {whoisError && (
            <p>
              <b>Whois Error:</b> {whoisError}
            </p>
          )}
          {rdapError && (
            <p>
              <b>RDAP Error:</b> {rdapError}
            </p>
          )}
          {securityError && (
            <p>
              <b>Security.txt Error:</b> {securityError}
            </p>
          )}
        </div>
      );
    } catch (err) {
      console.error(err);
      return <p>{t("ngen.lookup.no_summary")}</p>;
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Row className="align-items-center">
        <Col sm={12} lg={8}>
          <Form.Group controlId="formLookupInput">
            <Form.Label>{t("ngen.lookup.label")}</Form.Label>
            <Form.Control
              type="text"
              placeholder={t("ngen.lookup.placeholder")}
              value={inputValue}
              onChange={handleChange}
              required
              isInvalid={!validateAddressValueOrNetworkOrDomain(inputValue)}
            />
            <Form.Text className="text-muted">{t("ngen.lookup.help")}</Form.Text>
          </Form.Group>
        </Col>
        <Col sm={12} lg={4}>
          <Button variant="primary" type="submit" disabled={!validateAddressValueOrNetworkOrDomain(inputValue)}>
            {t("button.search")}
          </Button>
          <CrudButton type="cancel" />
        </Col>
      </Row>

      <Row className="mt-3">
        {taskStatus === "PENDING" && (
          <Row className="justify-content-center my-3">
            <Col xs="auto">
              <Spinner animation="border" variant="primary" role="status" />
            </Col>
          </Row>
        )}
        {taskStatus === "SUCCESS" && (
          <>
            <Alert variant="success">{renderSummary(taskResult)}</Alert>
            <Row className="mt-2">
              <Col sm={12}>
                <Accordion>
                  <Accordion.Item eventKey="0">
                    <Accordion.Header>{t("ngen.lookup.json_raw_result")}</Accordion.Header>
                    <Accordion.Body style={{ padding: 0, maxHeight: "500px", overflowY: "auto" }}>
                      <ReactJson
                        src={taskResult}
                        theme="monokai"
                        collapsed={2}
                        enableClipboard={false}
                        displayDataTypes={false}
                        displayObjectSize={false}
                        style={{ fontSize: "0.85rem", backgroundColor: "transparent" }}
                      />
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion>
              </Col>
            </Row>
          </>
        )}
        {taskStatus === "FAILURE" && <Alert variant="danger">{taskResult}</Alert>}
      </Row>
    </Form>
  );
};

export default FormLookup;
