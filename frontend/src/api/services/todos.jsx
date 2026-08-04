import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import i18next from "i18next";

const getTodosByEvent = (eventId, currentPage = 1, results = []) => {
  return (
    apiInstance
      // No ordering is asked for: the model orders the todos following the
      // procedure of each playbook
      .get(COMPONENT_URL.todo, { params: { event: eventId, page: currentPage } })
      .then((response) => {
        const res = [...results, ...response.data.results];
        if (response.data.next !== null) {
          return getTodosByEvent(eventId, currentPage + 1, res);
        }
        return res;
      })
      .catch((error) => {
        setAlert(i18next.t("ngen.todo.get.error"), "error", "todo");
        return Promise.reject(error);
      })
  );
};

const getTodo = (url) => {
  return apiInstance
    .get(url)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(i18next.t("ngen.todo.get.error"), "error", "todo");
      return Promise.reject(error);
    });
};

const patchTodo = (url, body) => {
  return apiInstance
    .patch(url, body)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(i18next.t("ngen.todo.edit.error"), "error", "todo");
      return Promise.reject(error);
    });
};

// Playbooks only reach an event when it is created or when its taxonomy
// changes, so a playbook written afterwards needs its tasks imported
const importPlaybookTasks = (eventId) => {
  return apiInstance
    .post(`${COMPONENT_URL.event}${eventId}/importplaybooktasks/`)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(i18next.t("ngen.todo.import.error"), "error", "todo");
      return Promise.reject(error);
    });
};

export { getTodosByEvent, getTodo, patchTodo, importPlaybookTasks };
