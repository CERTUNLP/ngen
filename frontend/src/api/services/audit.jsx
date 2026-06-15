import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const getAudits = (currentPage, filters, order) => {
  return apiInstance
    .get(`${COMPONENT_URL.audit}?page=${currentPage}&ordering=${order}&${filters}`)
    .then((response) => response)
    .catch((error) => {
      setAlert("Failed to fetch audit log", "error");
      return Promise.reject(error);
    });
};

const getObjectAudits = (modelName, objectId, page = 1) => {
  return apiInstance
    .get(`${COMPONENT_URL.audit}?content_type__model=${modelName}&object_id=${objectId}&ordering=-timestamp&page=${page}`)
    .then((response) => response)
    .catch(() => ({ data: { results: [], next: null } }));
};

export { getAudits, getObjectAudits };
