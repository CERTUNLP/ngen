import React, { useEffect, useState } from "react";
import { Row, Card } from "react-bootstrap";
import { APP_COMMIT, APP_BRANCH, APP_BUILD_FILE, APP_VERSION_TAG, MODE } from "config/constant";
import { getVersion } from "api/services/about";
import { useTranslation } from "react-i18next";

const InfoSection = ({ title, data }) => {
  const { t } = useTranslation();

  return (
    <Card>
      <Card.Header>
        <Card.Title as="h5">{title}</Card.Title>
      </Card.Header>
      <Card.Body>
        {data &&
          Object.keys(data).map((field) => (
            <p key={field}>
              {field.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}: {data[field] || t("w.not_available")}
            </p>
          ))}
      </Card.Body>
    </Card>
  );
};

const About = () => {
  const [about, setAbout] = useState({ backend: {} });
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
          <InfoSection title="Backend" data={{ ...about }} />
        </div>
      </Row>
    </>
  );
};

export default About;
