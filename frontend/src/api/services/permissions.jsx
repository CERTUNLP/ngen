import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const getPermission = (url) => {
  return apiInstance.get(url);
};

const getMinifiedPermissions = () => {
  let messageError = `No se pudo recuperar la informacion de los permisos`;
  return apiInstance
    .get(COMPONENT_URL.permissionMinifiedList)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      setAlert(messageError, "error");
      return Promise.reject(error);
    });
};


export { getPermission, getMinifiedPermissions };
