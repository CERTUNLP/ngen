import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "../../config/constant";
import setAlert from "../../utils/setAlert";


const getAllAnalyzerMappings = () => {
  return apiInstance
    .get(COMPONENT_URL.analyzerMapping)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};


const getAnalyzerMappings = (currentPage, filters, order) => {
  let messageError = `No se pudo recuperar la informacion de los mapeos`;
  return apiInstance
    .get(COMPONENT_URL.analyzerMapping + PAGE + currentPage + "&ordering=" + order + "&" + filters)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "analyzermapping");
      return Promise.reject(error);
    });
};


const postAnalyzerMapping = (data) => {
  const messageError = `Ya existe un mapeo con los mismos valores.`;
  const messageSuccess = `El mapeo ha sido creado correctamente.`;

  const filters = `mapping_to__icontains=${data.mapping_to}&mapping_from__name__icontains=${data.mapping_from_name}&analyzer_type=${data.analyzer_type}`;
  return getAnalyzerMappings(1, filters, "date")
    .then((response) => {
      if (response.data.results.length > 0) {
        setAlert(messageError, "error", "analyzermapping");
        return Promise.reject(new Error(messageError));
      }

      return apiInstance
        .post(COMPONENT_URL.analyzerMapping, {
          mapping_to: data.mapping_to,
          mapping_from: data.mapping_from,
          analyzer_type: data.analyzer_type,
        })
        .then((response) => {
          setAlert(messageSuccess, "success", "analyzermapping");
          return response;
        });
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};


const getAnalyzerMapping = (url) => {
  let messageError = `No se pudo recuperar la informacion del mapeo`;
  return apiInstance
    .get(url)
    .then((response) => {
      return apiInstance
        .get(response.data.mapping_from)
        .then((mappingResponse) => {
          response.data.mapping_from_name = mappingResponse.data.name;
          return response;
        });
    })
    .catch((error) => {
      setAlert(messageError, "error", "analyzermapping");
      return Promise.reject(error);
    });
};

const putAnalyzerMapping = (url, data) => {
  const messageSuccess = `El mapeo ha sido editado correctamente.`;
  const messageError = `Ya existe un mapeo con los mismos valores.`;
  const notFoundError = `El mapeo no se ha encontrado.`;

  const filters = `mapping_to__icontains=${data.mapping_to}&mapping_from__name__icontains=${data.mapping_from_name}&analyzer_type=${data.analyzer_type}`;
  return getAnalyzerMappings(1, filters, "date")
    .then((response) => {
      console.log("Response data:", response.data.results.length > 0);
      if (response.data.results.length > 0) {
        setAlert(messageError, "error", "analyzermapping");
        return Promise.reject(new Error(messageError));
      }

      return apiInstance
        .put(url, {
          mapping_to: data.mapping_to,
          mapping_from: data.mapping_from,
          analyzer_type: data.analyzer_type,
        })
        .then((response) => {
          setAlert(messageSuccess, "success", "analyzermapping");
          return response;
        });
    })
    .catch((error) => {
      if (error.response?.detail === "Not found") {
        setAlert(notFoundError, "error", "analyzermapping");
      } else {
        setAlert(messageError, "error", "analyzermapping");
      }
      return Promise.reject(error);
    });
};


const deleteAnalyzerMapping = (url, name_from, name_to, analyzer) => {
  let messageSuccess = `El mapeo de ${name_from} a ${name_to} del analizador ${analyzer} ha sido eliminado.`;
  let messageError = `El mapeo de ${name_from} a ${name_to} del analizador ${analyzer} no se ha encontrado.`;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, "success", "analyzerMapping");
      return response;
    })
    .catch((error) => {
      if (error.response.detail && error.response.detail === "Not found") {
        messageError = `El mapeo de ${name_from} a ${name_to} del analizador ${analyzer} no se ha encontrado.`;
      }
      setAlert(messageError, "error", "analyzerMapping");
      return Promise.reject(error);
    });
};

  
export { getAllAnalyzerMappings, getAnalyzerMappings, postAnalyzerMapping, getAnalyzerMapping, putAnalyzerMapping, deleteAnalyzerMapping };