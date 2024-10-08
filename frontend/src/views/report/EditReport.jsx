import React, { useEffect, useState } from "react";
import { Card, Row, Spinner } from "react-bootstrap";
import { useLocation } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import FormReport from "./components/FormReport";
import { putReport } from "../../api/services/reports";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { useTranslation } from "react-i18next";

const EditReport = () => {
  const location = useLocation();
  const fromState = location.state;
  const [body, setBody] = useState(fromState);
  const [taxonomies, setTaxonomies] = useState([]);
  const { t } = useTranslation();

  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    getMinifiedTaxonomy()
      .then((response) => {
        let listTaxonomies = response.map((taxonomy) => {
          return { value: taxonomy.url, label: taxonomy.name };
        });
        setTaxonomies(listTaxonomies);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const editReport = () => {
    putReport(
      body.url,
      body.problem,
      body.derived_problem,
      body.verification,
      body.recommendations,
      body.more_information,
      body.lang,
      body.taxonomy
    )
      .then((response) => {
        window.location.href = "/reports";
      })
      .catch((error) => {
        setShowAlert(true);
      });
  };

  return (
    <div>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("ngen.report.edit")}</Card.Title>
        </Card.Header>
        <Card.Body>
          {loading && <Spinner animation="border" variant="primary" />}
          <FormReport body={body} setBody={setBody} taxonomies={taxonomies} createOrEdit={editReport} />
        </Card.Body>
      </Card>
    </div>
  );
};

export default EditReport;
