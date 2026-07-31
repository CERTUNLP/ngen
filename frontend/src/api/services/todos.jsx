import apiInstance from "../api";
import { COMPONENT_URL } from "../../config/constant";
import setAlert from "../../utils/setAlert";
import i18next from "i18next";

// Same order the playbook gives to its tasks: most severe priority first
const TODO_ORDERING = "task__priority__severity,id";

const getTodosByEvent = (eventId, currentPage = 1, results = []) => {
  return apiInstance
    .get(COMPONENT_URL.todo, { params: { event: eventId, page: currentPage, ordering: TODO_ORDERING } })
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
    });
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

export { getTodosByEvent, getTodo, patchTodo };
