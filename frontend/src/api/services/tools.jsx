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

const getAddressInfo = (ip_or_domain, { with_contacts = true, with_networks = false, with_entity = false, with_events = false } = {}) => {
  return apiInstance
    .post(COMPONENT_URL.addressinfo, { ip_or_domain, with_contacts, with_networks, with_entity, with_events })
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getTask = (url) => {
  return apiInstance.get(url);
};

export { lookup, getAddressInfo, getTask };
