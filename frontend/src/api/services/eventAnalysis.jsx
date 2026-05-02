import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import i18next from "i18next";

const getRetests = (eventUrl, suppressAlert) => {
  const messageSuccess = i18next.t("ngen.retest.refresh.success");
  const messageError = i18next.t("ngen.retest.refresh.error");

  return apiInstance
    .get(COMPONENT_URL.eventAnalysis + "?page_size=1000&ordering=-date")
    .then((response) => {
      const filteredResults = response.data.results.filter((item) => item.event === eventUrl);
      if (!suppressAlert) {
        setAlert(messageSuccess, "success", "retest");
      }
      return filteredResults;
    })
    .catch((error) => {
      if (!suppressAlert) { 
        setAlert(messageError, "error");
      }
      return Promise.reject(error);
    });
};

const postRetest = (eventId, analyzerMapping = null) => {
  const messageSuccess = i18next.t("ngen.retest.success");
  const messageError = i18next.t("ngen.retest.error");
  return apiInstance
    .post(`${COMPONENT_URL.event}${eventId}/retest/`, {
      analyzer_mapping: analyzerMapping,
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "retest");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "retest");
      return Promise.reject(error);
    });
};


export { getRetests, postRetest };