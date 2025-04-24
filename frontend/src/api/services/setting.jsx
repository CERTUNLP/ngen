import apiInstance from "../api";
import { COMPONENT_URL, PAGE, SETTING } from "../../config/constant";
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
  let messageError = `No se pudo recuperar la informacion de la configuracion`;
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

const patchSetting = (url, key, value) => {
  let messageSuccess = `Configuracion guardada con exito.`;
  let messageError = `No se ha podido guardar la configuracion. `;

  return apiInstance
    .patch(url, {
      value: value
    })
    .then((response) => {
      updateConfigs(key, value);
      setAlert(messageSuccess, "success", "setting");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "setting");
      return Promise.reject(error);
    });
};

function updateConfigs(key, value) {
  localStorage.setItem(key, value);
  if (key === "NGEN_LANG") {
    i18n.changeLanguage(value);
  }
}

const getValue = (key, defaultValue = undefined, cached = true) => {
  if (cached) {
    const cachedValue = localStorage.getItem(key);
    if (cachedValue !== null && cachedValue !== undefined) {
      return Promise.resolve(cachedValue);
    }
  }

  let messageError = `No se pudo recuperar la información de la configuración`;
  return apiInstance
    .get(COMPONENT_URL.configPublic)
    .then((response) => {
      response.data.forEach((item) => {
        localStorage.setItem(item.key, item.value);
      });
      const fetchedValue = response.data.find((item) => item.key === key);
      const value = fetchedValue ? fetchedValue.value : defaultValue;
      return value;
    })
    .catch((error) => {
      setAlert(messageError, "error", "state");
      return Promise.reject(error);
    });
};
const getSettingLanguage = () => getValue(SETTING.NGEN_LANG);

const getSettingPageSize = () => getValue(SETTING.PAGE_SIZE).then((val) => parseInt(val));

const getSettingJWTRefreshTokenLifetime = (cached = true) =>
  getValue(SETTING.JWT_REFRESH_TOKEN_LIFETIME, undefined, cached).then((val) => parseInt(val));

const uploadTeamLogo = (file) => {
  let messageSuccess = `Logo del equipo subido con exito.`;
  let messageError = `No se ha podido subir el logo del equipo. `;

  const formData = new FormData();
  formData.append("file", file);

  return apiInstance
    .put(COMPONENT_URL.constanceUploadTeamLogo, formData)
    .then((response) => {
      setAlert(messageSuccess, "success", "team");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "team");
      return Promise.reject(error);
    });
};

export {
  getAllSetting,
  patchSetting,
  getSetting,
  getSettingPageSize,
  uploadTeamLogo,
  getValue,
  getSettingLanguage,
  getSettingJWTRefreshTokenLifetime
};
