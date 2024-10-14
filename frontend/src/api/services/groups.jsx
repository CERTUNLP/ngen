import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const getGroup = (url) => {
  return apiInstance.get(url);
};

const getMinifiedGroups = () => {
  let messageError = `No se pudo recuperar la informacion de los grupos`;
  return apiInstance
    .get(COMPONENT_URL.groupMinifiedList)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      setAlert(messageError, "error");
      return Promise.reject(error);
    });
};


export { getGroup, getMinifiedGroups };
