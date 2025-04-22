import React, { useEffect, useState } from "react";
import { Button, Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import TableRetests from "./TableRetests";
import { getRetests, postRetest } from "../../../api/services/eventAnalysis";
import Alert from "components/Alert/Alert";
import { getAnalyzerMappings } from "../../../api/services/analyzerMapping";

const SmallRetestTable = ({ retests, eventId, eventUrl, taxonomyUrl }) => {
  const { t } = useTranslation();
  const [retestItems, setRetestItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAlert, setShowAlert] = useState(false); 
  const [alertMessage, setAlertMessage] = useState(""); 
  const [alertType, setAlertType] = useState("success"); 
  const [hasAnalyzerMapping, setHasAnalyzerMapping] = useState(true);
  const [isRefreshDisabled, setIsRefreshDisabled] = useState(false);

  useEffect(() => {
    const sortedRetests = (retests || []).sort(
      (a, b) => new Date(b.date) - new Date(a.date)
    );
    setRetestItems(sortedRetests);
  }, [retests]);


  useEffect(() => {
    const checkAnalyzerMapping = async () => {
      try {
        const mappings = await getAnalyzerMappings();
        const isMapped = mappings.results.some(
          (mapping) => mapping.mapping_from === taxonomyUrl
        );
        setHasAnalyzerMapping(isMapped);
      } catch (error) {
        console.error("Error checking analyzer mappings:", error);
        setHasAnalyzerMapping(false);
      }
    };

    if (taxonomyUrl) {
      checkAnalyzerMapping();
    }
  }, [taxonomyUrl]);


  const handleRetest = async () => {
    try {
      const response = await postRetest(eventId);
      if (response) {
        setAlertMessage(t("ngen.retest.success"));
        setAlertType("success");
        setShowAlert(true);
        refreshRetests();
      }
    } catch (error) {
      setAlertMessage(t("ngen.retest.error"));
      setAlertType("error");
      setShowAlert(true);
    }
  };

  const refreshRetests = async () => {
    setIsLoading(true);
    setIsRefreshDisabled(true);
    console.log("Refresh Retests");
    try {
      const response = await getRetests(eventUrl);
      const sortedRetests = (response || []).sort(
        (a, b) => new Date(b.date) - new Date(a.date)
      );
      if (response) {
        setRetestItems(sortedRetests);
        setAlertMessage(t("ngen.retest.refresh.success"));
        setShowAlert(true);
      }
    } catch (error) {
      setAlertMessage(t("ngen.retest.refresh.error"));
      setAlertType("error");
      setShowAlert(true);
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        setIsRefreshDisabled(false);
      }, 3000);
    }
  };

  const isRetestInProgress = retestItems.some((retest) => retest.result === "in_progress");

  return (
    <React.Fragment>
      <Alert
        show={showAlert}
        onClose={() => setShowAlert(false)}
        message={alertMessage}
        type={alertType}
        duration={3000}
      />
      <Card>
        <Card.Header>
          <div className="d-flex align-items-center">
            <Card.Title as="h5" className="mb-0">
              {t("ngen.retests")}
            </Card.Title>
            {hasAnalyzerMapping && (
              <>
                <Button
                  size="sm"
                  variant="outline-dark"
                  className="rounded-circle ms-3"
                  onClick={refreshRetests}
                  title={t("ngen.retest.refresh")}
                  disabled={isLoading || isRefreshDisabled}
                >
                  <i className="fa fa-sync-alt"></i>
                </Button>
                <Button
                  size="sm"
                  variant="outline-dark"
                  className="rounded-circle ms-3"
                  onClick={handleRetest}
                  title={t("ngen.retest.create")}
                  disabled={isRetestInProgress}
                >
                  <i className="fa fa-tools"></i>
                </Button>
              </>
            )}
          </div>
        </Card.Header>
        <Card.Body>
          {!hasAnalyzerMapping ? (
            <p>{t("ngen.retest.no_analyzer_mapping")}</p>
          ) : retestItems.length === 0 ? (
            <p>{t("ngen.no_retests")}</p>
          ) : (
            <TableRetests retests={retestItems} />
          )}
        </Card.Body>
      </Card>
    </React.Fragment>
  );
};

export default SmallRetestTable;