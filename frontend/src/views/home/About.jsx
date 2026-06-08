import React, { useEffect, useState } from "react";
import { Row, Card, Badge } from "react-bootstrap";
import { APP_COMMIT, APP_BRANCH, APP_BUILD_FILE, APP_VERSION_TAG, MODE } from "config/constant";
import { getVersion } from "api/services/about";
import { useTranslation } from "react-i18next";

const QueueStats = ({ data }) => {
  const { t } = useTranslation();
  const entries = [
    { key: "pending", label: t("ngen.email_queue.pending"), variant: "info" },
    { key: "sent_today", label: t("ngen.email_queue.sent_today"), variant: "success" },
    { key: "failed", label: t("ngen.email_queue.failed"), variant: "danger" },
    { key: "total", label: t("ngen.email_queue.total"), variant: "secondary" },
  ];

  return (
    <Card>
      <Card.Header>
        <Card.Title as="h5">
          {t("ngen.email_queue.title")}{" "}
          {data.auto_send ? (
            <Badge bg="success" className="ms-1">{t("ngen.email_queue.auto_send")}</Badge>
          ) : (
            <Badge bg="warning" className="ms-1">{t("ngen.email_queue.manual_send")}</Badge>
          )}
        </Card.Title>
      </Card.Header>
      <Card.Body>
        <Row>
          {entries.map(({ key, label, variant }) => (
            <div className="col-4 col-md-2 text-center mb-3" key={key}>
              <h3>
                <Badge bg={variant} className="w-100 py-2">
                  {data[key] ?? 0}
                </Badge>
              </h3>
              <small className="text-muted">{label}</small>
            </div>
          ))}
        </Row>
      </Card.Body>
    </Card>
  );
};

const InfoSection = ({ title, data }) => {
  const { t } = useTranslation();

  const formatValue = (key, value) => {
    if (typeof value === "object" && value !== null) {
      return JSON.stringify(value);
    }
    return value ?? t("w.not_available");
  };

  return (
    <Card>
      <Card.Header>
        <Card.Title as="h5">{title}</Card.Title>
      </Card.Header>
      <Card.Body>
        {data &&
          Object.keys(data)
            .filter((field) => !["email_queue"].includes(field))
            .map((field) => (
              <p key={field}>
                {field.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}: {formatValue(field, data[field])}
              </p>
            ))}
      </Card.Body>
    </Card>
  );
};

const About = () => {
  const [about, setAbout] = useState({ backend: {}, email_queue: {} });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { t } = useTranslation();

  useEffect(() => {
    getVersion()
      .then((value) => {
        setAbout(value);
      })
      .catch((error) => {
        console.error("Error fetching version:", error);
        setError(error);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading || error) {
    return (
      <div className="container">
        {loading && <p>Loading...</p>}
        {error && <p>Error: {error.message}</p>}
      </div>
    );
  }

  return (
    <>
      <h1>{t("w.about")}</h1>
      <Row className="mb-4">
        <div className="col-md-6">
          <InfoSection
            title="Frontend"
            data={{ version: APP_VERSION_TAG, commit: APP_COMMIT, branch: APP_BRANCH, build_file: APP_BUILD_FILE, environment: MODE }}
          />
        </div>
        <div className="col-md-6">
          <InfoSection title="Backend" data={{ version: about.version, commit: about.commit, branch: about.branch, environment: about.environment }} />
        </div>
      </Row>
      <Row className="mb-4">
        <div className="col-12">
          <QueueStats data={about.email_queue || {}} />
        </div>
      </Row>
    </>
  );
};

export default About;
