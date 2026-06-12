import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "../../config/constant";
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

const getGroups = (currentPage, filters, order) => {
  let messageError = `No se pudo recuperar la informacion de los grupos`;
  return apiInstance
    .get(COMPONENT_URL.group + PAGE + currentPage + "&ordering=" + order + "&" + filters)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error");
      return Promise.reject(error);
    });
};

const getAllGroups = (currentPage = 1, results = [], limit = 100) => {
  let messageError = `No se pudo recuperar la informacion de los grupos`;
  return apiInstance
    .get(COMPONENT_URL.group, { params: { page: currentPage, page_size: limit } })
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllGroups(++currentPage, res, limit);
      } else {
        return res;
      }
    })
    .catch((error) => {
      setAlert(messageError, "error");
      return Promise.reject(error);
    });
};

const postGroup = (name, permissions) => {
  let messageSuccess = `El grupo ${name} se ha creado correctamente`;
  let messageError = `El grupo ${name} no se pudo crear`;
  return apiInstance
    .post(COMPONENT_URL.group, {
      name: name,
      permissions: permissions
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "group");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "group");
      return Promise.reject(error);
    });
};

const putGroup = (url, name, permissions) => {
  let messageSuccess = `El grupo ${name} se ha editado correctamente`;
  let messageError = `El grupo ${name} no se pudo editar`;
  return apiInstance
    .put(url, {
      name: name,
      permissions: permissions
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "group");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "group");
      return Promise.reject(error);
    });
};

const deleteGroup = (url, name) => {
  let messageSuccess = `El grupo ${name} se ha eliminado correctamente`;
  let messageError = `El grupo ${name} no se pudo eliminar`;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, "success", "group");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "group");
      return Promise.reject(error);
    });
};

export { getGroup, getMinifiedGroups, getGroups, getAllGroups, postGroup, putGroup, deleteGroup };
