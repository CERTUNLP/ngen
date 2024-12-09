import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "../../config/constant";
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

const getTags = (currentPage, filters, order) => {
  return apiInstance.get(COMPONENT_URL.tag + PAGE + currentPage + "&ordering=" + order + "&" + filters)
};

const getTag = (url) => {
  return apiInstance.get(url);
};

const deleteTag = (url) => {
  return apiInstance
    .delete(url)
    .then((response) => {
      // setAlert(i18next.t("ngen.tag.delete"), "success", "tag");
      return response;
    })
    .catch((error) => {
      setAlert(error.response.statusText, "error", "tag");
      return Promise.reject(error);
    });
};

const postTag = (value, color, avoidRaise = false) => {
  return apiInstance
    .post(COMPONENT_URL.tag, {
      name: value,
      color: color
    }, { avoidRaise: avoidRaise })
    .then((response) => {
      setAlert(i18next.t("w.creation_success"), "success", "tag");
      return response;
    })
    .catch((error) => {
      if (avoidRaise) {
        return Promise.reject(error);
      }
      let statusText = error.response.statusText;
      setAlert(statusText, "error", "tag");
      return Promise.reject(error);
    });
};

const patchTag = (url, value, color) => {
  return apiInstance
    .patch(url, {
      name: value,
      color: color
    })
};

export { getTags, postTag, getTag, getMinifiedTag, patchTag, deleteTag };
