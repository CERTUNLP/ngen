import apiInstance from "../api";
import setAlert from "../../utils/setAlert";
import { COMPONENT_URL, PAGE } from "../../config/constant";
import i18next from "i18next";

const getTasks = (currentPage) => {
  return apiInstance
    .get(COMPONENT_URL.task + PAGE + currentPage)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getAllTasks = (currentPage = 1, results = [], limit = 100) => {
  return apiInstance
    .get(COMPONENT_URL.task, { params: { page: currentPage } }) //, page_size: limit
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllTasks(++currentPage, res, limit);
      } else {
        return res;
      }
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getTask = (url) => {
  let messageError = `No se ha recuperado informacion de la tarea. `;
  return apiInstance
    .get(url)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "playbook");
      return Promise.reject(error);
    });
};

const postTask = (name, description, priority, playbook) => {
  let messageSuccess = `La tarea ${name} se ha creado correctamente.`;
  let messageError = `La tarea ${name} no se ha creado. `;
  return apiInstance
    .post(COMPONENT_URL.task, {
      name: name,
      description: description,
      priority: priority,
      playbook: playbook
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "playbook");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "playbook");
      return Promise.reject(error);
    });
};

const putTask = (url, name, description, priority, playbook) => {
  let messageSuccess = `La tarea ${name} se ha editado correctamente.`;
  let messageError = `La tarea ${name} no se ha editado. `;
  return apiInstance
    .put(url, {
      name: name,
      description: description,
      priority: priority,
      playbook: playbook
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "playbook");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "playbook");
      return Promise.reject(error);
    });
};

const deleteTask = (url, name) => {
  let messageSuccess = `La tarea ${name} se ha eliminado correctamente. `;
  let messageError = `La tarea ${name} no se ha eliminado. `;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, "success", "playbook");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "playbook");
      return Promise.reject(error);
    });
};

// The order of the tasks is the order of the procedure, so it is moved one
// position at a time instead of being derived from the priority
const moveTask = (url, direction) => {
  return apiInstance
    .post(`${url}move/`, { direction: direction })
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(i18next.t("ngen.task.move.error"), "error", "playbook");
      return Promise.reject(error);
    });
};

export { getTasks, getAllTasks, getTask, postTask, putTask, deleteTask, moveTask };
