import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "../../config/constant";
import setAlert from "../../utils/setAlert";

const getMinifiedTaxonomyGroups = () => {
  let messageError = `No se pudo recuperar la informacion de los grupos de taxonomias`;
  return apiInstance
    .get(COMPONENT_URL.taxonomyGroupMinifiedList)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      setAlert(messageError, "error", "taxonomy group");
      return Promise.reject(error);
    });
};

const getTaxonomyGroups = (currentPage, filters, order) => {
  let messageError = `No se pudo recuperar la informacion del grupo de taxonomias`;
  return apiInstance
    .get(COMPONENT_URL.taxonomyGroup + PAGE + currentPage + "&ordering=" + order + "&" + filters)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

const getTaxonomyGroup = (url) => {
  let messageError = `No se pudo recuperar la informacion del grupo de taxonomia`;
  return apiInstance
    .get(url)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

const getAllTaxonomyGroups = (currentPage = 1, results = [], limit = 100) => {
  let messageError = `No se pudo recuperar la informacion del grupo de taxonomias`;
  return apiInstance
    .get(COMPONENT_URL.taxonomyGroup, { params: { page: currentPage } }) //, page_size: limit
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllTaxonomyGroups(++currentPage, res, limit);
      } else {
        res.sort((p, q) => {
          return p.slug > q.slug ? 1 : -1;
        });
        return res;
      }
    })
    .catch((error) => {
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

const postTaxonomyGroup = (name, description, needs_review, group) => {
  let messageSuccess = `El grupo de taxonomia ${name} se ha creado correctamente`;
  let messageError = `El grupo de taxonomia ${name} no ha creado. `;
  return apiInstance
    .post(COMPONENT_URL.taxonomyGroup, {
      name: name,
      description: description,
      needs_review: needs_review,
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "taxonomy");
      return response;
    })
    .catch((error) => {
      //"slug": ["Ya existe una entidad Taxonomy con slug=copyright." ],
      console.log(error);

      let statusText = "";
      if (error.response.status === 400) {
        console.log("status 400");
        if (error.response.data.slug && error.response.data.slug[0].includes("Ya existe una entidad Taxonomy con slug")) {
          statusText = "Ingrese un nombre diferente.";
          console.log("Error de slug");
        }
      }

      messageError += statusText;
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

const putTaxonomyGroup = (url, name, description, needs_review) => {
  let messageSuccess = `El grupo de taxonomia ${name} se ha editado correctamente`;
  let messageError = `El grupo de taxonomia ${name} no se ha editado. `;
  return apiInstance
    .put(url, {
      name: name,
      description: description,
      needs_review: needs_review,
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "taxonomy");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

const putActivationStatus = (url, state, name) => {
  let messageSuccess = !state ? `El grupo de taxonomia ${name} ha sido desactivada` : `El grupo de taxonomia ${name} ha sido activada`;
  let messageError = `El grupo de taxonomia ${name} no se pudo modificar`;
  return apiInstance
    .patch(url, {
      active: state
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "taxonomy");
      return response;
    })
    .catch((error) => {
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

const deleteTaxonomyGroup = (url, name) => {
  let messageSuccess = `El grupo de taxonomia ${name} se ha eliminado correctamente`;
  let messageError = `El grupo de taxonomia ${name} no se ha encontrado.`;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, "success", "taxonomy");
      return response;
    })
    .catch((error) => {
      if (error.response.detail && error.response.detail === "Not found") {
        messageError = `El grupo de taxonomia ${name} no se ha encontrado.`;
      }
      setAlert(messageError, "error", "taxonomy");
      return Promise.reject(error);
    });
};

export {
  getTaxonomyGroups,
  getTaxonomyGroup,
  getAllTaxonomyGroups,
  postTaxonomyGroup,
  putTaxonomyGroup,
  putActivationStatus,
  deleteTaxonomyGroup,
  getMinifiedTaxonomyGroups
};
