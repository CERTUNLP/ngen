import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const lookup = (value) => {
  return apiInstance
    .post(COMPONENT_URL.lookup, { ip_or_domain: value })
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      setAlert("Error al realizar la búsqueda", "error");
      return Promise.reject(error);
    });
};

const getTask = (url) => {
  return apiInstance.get(url);
};

export { lookup, getTask };
