import apiInstance from "../api";
import { COMPONENT_URL, PAGE, PAGE_SIZE } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const getAllSetting = (currentPage = 1, results = [], limit = 100) => {
  return apiInstance
    .get(COMPONENT_URL.constance, {
      params: {
        page: currentPage,
        page_size: limit
      }
    })
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllSetting(++currentPage, res, limit);
      } else {
        return res;
      }
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getSetting = (currentPage) => {
  //el parametro es para completar la url con el numero de pagina
  let messageError = `No se pudo recuperar la informacion de los estados`;
  return apiInstance
    .get(COMPONENT_URL.constance + PAGE + currentPage)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "state");
      return Promise.reject(error);
    });
};

const patchSetting = (url, value) => {
  let messageSuccess = `Los eventps han sido mergeados correctamente.`;
  let messageError = `Los eventos no han sido mergeados. `;

  return apiInstance
    .patch(url, {
      value: value
    })
    .then((response) => {
      setAlert(messageSuccess, "success");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error");
      return Promise.reject(error);
    });
};

const settingPageSize = () => {
  const cacheKey = `page_size`;
  const cachedPageSize = localStorage.getItem(cacheKey);

  if (cachedPageSize) {
    return Promise.resolve(cachedPageSize);
  }

  let messageError = `No se pudo recuperar la información del tamaño de página`;
  return apiInstance
    .get(COMPONENT_URL.constance + PAGE_SIZE)
    .then((response) => {
      // Almacenar en localStorage
      localStorage.setItem(cacheKey, response.data.value);
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "state");
      return Promise.reject(error);
    });
};

export { getAllSetting, patchSetting, getSetting, settingPageSize };
