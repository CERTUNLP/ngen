import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const getAllAnalyzers = () => {
  return apiInstance
    .get(COMPONENT_URL.analyzer + "?page_size=1000")
    .then((response) => response.data.results)
    .catch((error) => {
      setAlert("No se pudo recuperar la lista de analizadores", "error", "analyzer");
      return Promise.reject(error);
    });
};

const getAnalyzers = (currentPage, filters, order) => {
  return apiInstance
    .get(COMPONENT_URL.analyzer + PAGE + currentPage + "&ordering=" + order + "&" + filters)
    .then((response) => response)
    .catch((error) => {
      setAlert("No se pudo recuperar la lista de analizadores", "error", "analyzer");
      return Promise.reject(error);
    });
};

const getAnalyzer = (url) => {
  return apiInstance
    .get(url)
    .then((response) => response)
    .catch((error) => {
      setAlert("No se pudo recuperar el analizador", "error", "analyzer");
      return Promise.reject(error);
    });
};

const postAnalyzer = (data) => {
  return apiInstance
    .post(COMPONENT_URL.analyzer, data)
    .then((response) => {
      setAlert(`El analizador ${data.name} fue creado correctamente`, "success", "analyzer");
      return response;
    })
    .catch((error) => {
      setAlert(`No se pudo crear el analizador ${data.name}`, "error", "analyzer");
      return Promise.reject(error);
    });
};

const putAnalyzer = (url, data) => {
  return apiInstance
    .put(url, data)
    .then((response) => {
      setAlert(`El analizador ${data.name} fue actualizado correctamente`, "success", "analyzer");
      return response;
    })
    .catch((error) => {
      setAlert(`No se pudo actualizar el analizador ${data.name}`, "error", "analyzer");
      return Promise.reject(error);
    });
};

const deleteAnalyzer = (url, name) => {
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(`El analizador ${name} fue eliminado correctamente`, "success", "analyzer");
      return response;
    })
    .catch((error) => {
      setAlert(`No se pudo eliminar el analizador ${name}`, "error", "analyzer");
      return Promise.reject(error);
    });
};

const testAnalyzerConnection = (url) => {
  return apiInstance
    .post(url + "test/")
    .then((response) => response)
    .catch((error) => Promise.reject(error));
};

const getVulnChoices = () => {
  return apiInstance
    .get(COMPONENT_URL.analyzer + "vuln-choices/")
    .then((response) => response.data)
    .catch((error) => Promise.reject(error));
};

export { getAllAnalyzers, getAnalyzers, getAnalyzer, postAnalyzer, putAnalyzer, deleteAnalyzer, testAnalyzerConnection, getVulnChoices };
