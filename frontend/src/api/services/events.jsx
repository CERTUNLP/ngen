import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import i18next from "i18next";

const getEvents = (currentPage, filters, order, asNetworkAdmin) => {
  //el parametro es para completar la url con el numero de pagina
  let component = asNetworkAdmin ? COMPONENT_URL.networkadminEvent : COMPONENT_URL.event;
  if (!filters.includes("parent__isnull")) {
    filters += "parent__isnull=true&";
  }
  return apiInstance.get(component + PAGE + currentPage + "&ordering=" + order + "&" + filters);
};

const postEvent = (formData) => {
  //el parametro es para completar la url con el numero de pagina
  let messageSuccess = i18next.t("ngen.create.event.success");
  let messageError = i18next.t("ngen.create.event.error");

  return apiInstance
    .post(COMPONENT_URL.event, formData)
    .then((response) => {
      setAlert(messageSuccess, "success", "event");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "event");
      return Promise.reject(error);
    });
};

const putEvent = (url, formData) => {
  //el parametro es para completar la url con el numero de pagina
  let messageSuccess = i18next.t("ngen.edit.event.success");
  let messageError = i18next.t("ngen.edit.event.error");
  return apiInstance
    .put(url, formData)
    .then((response) => {
      setAlert(messageSuccess, "success", "event");
      return response;
    })
    .catch((error) => {
      console.log(error.response.data._detail);
      if (error.response.data._detail.includes("already exists")) {
        messageError += `. ${i18next.t("ngen.edit.event.error.file")}`;
        setAlert(messageError, "error", "event");
      }
      return Promise.reject(error);
    });
};

const patchEvent = (url, formData) => {
  //el parametro es para completar la url con el numero de pagina
  let messageSuccess = i18next.t("ngen.edit.event.success");
  let messageError = i18next.t("ngen.edit.event.error");

  return apiInstance
    .patch(url, formData)
    .then((response) => {
      setAlert(messageSuccess, "success", "event");
      return response;
    })
    .catch((error) => {
      console.log("error", error);
      if (error.response?.data) {
        for (let key in error.response.data) {
          let keystr = key === "__all__" || key === "detail" ? "" : `${key}: `;
          messageError += `. ${keystr}${error.response.data[key]}`;
        }
      }
      setAlert(messageError, "error", "event");
      return Promise.reject(error);
    });
};

const getEvent = (url) => {
  //el parametro es para completar la url con el numero de pagina
  return apiInstance.get(url);
};

const deleteEvent = (url) => {
  let messageSuccess = i18next.t("ngen.delete.event.success");
  let messageError = i18next.t("ngen.delete.event.error");
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, "success", "event");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "event");
      return Promise.reject(error);
    });
};

const mergeEvent = (urlParent, urlChildren) => {
  return patchEvent(urlChildren, { parent: urlParent });
};

const getAllEvents = (currentPage = 1, results = [], limit = 100) => {
  return apiInstance
    .get(COMPONENT_URL.event, { params: { page: currentPage } }) //, page_size: limit
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllEvents(++currentPage, res, limit);
      } else {
        res.sort((p, q) => {
          return p.slug > q.slug ? 1 : -1;
        });
        return res;
      }
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getListEvents = (list) => {
  const listEvents = [];
  list.forEach(function (url) {
    apiInstance
      .get(url)
      .then((response) => {
        listEvents.push(response.data);
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  });
  return list;
};

const getQueryEvent = async () => {
  const response = await getAllEvents();

  // Transform the response into a dictionary
  const dicEvents = {};
  response.forEach((event) => {
    dicEvents[event.url] = event;
  });

  // Return the transformed dictionary (this will be cached)
  return dicEvents;
};

const markSolved = (uuid) => {
  // Example path: /api/event/marksolved/<UUID>
  //el parametro es para completar la url con el numero de pagina
  let messageSuccess = i18next.t("ngen.edit.event.success");
  let messageError = i18next.t("ngen.edit.event.error");

  return apiInstance
    .post(`${COMPONENT_URL.event}marksolved/${uuid}/`)
    .then((response) => {
      setAlert(messageSuccess, "success", "event");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "event");
      return Promise.reject(error);
    });
};

export { getEvents, postEvent, putEvent, deleteEvent, mergeEvent, getEvent, getAllEvents, getListEvents, patchEvent, markSolved, getQueryEvent };
