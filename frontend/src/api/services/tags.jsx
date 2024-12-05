import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import i18next from "i18next";

const getMinifiedTag = () => {
  //el parametro es para completar la url con el numero de pagina
  let messageError = i18next.t("ngen.tag.error");
  return apiInstance
    .get(COMPONENT_URL.tagMinifiedList)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      setAlert(messageError, "error", "case");
      return Promise.reject(error);
    });
};

const getTags = (page = "") => {
  return apiInstance.get(COMPONENT_URL.tag + page);
};

const getTag = (url) => {
  return apiInstance.get(url);
};

const postTag = (type, value) => {
  return apiInstance.post(COMPONENT_URL.tag, {
    type: type,
    value: value
  });
};

export { getTags, postTag, getTag, getMinifiedTag };
