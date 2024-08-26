import apiInstance from '../api';
import setAlert from '../../utils/setAlert';
import { COMPONENT_URL, PAGE } from '../../config/constant';

const getEdges = (currentPage) => {
  return apiInstance
    .get(COMPONENT_URL.edge + PAGE + currentPage)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getAllEdges = (currentPage = 1, results = [], limit = 100) => {
  return apiInstance
    .get(COMPONENT_URL.edge, { params: { page: currentPage } }) //, page_size: limit
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllEdges(++currentPage, res, limit);
      } else {
        return res;
      }
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const getEdge = (url) => {
  let messageError = `No se ha recuperado informacion . `;
  return apiInstance
    .get(url)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      setAlert(messageError, 'error', 'state');
      return Promise.reject(error);
    });
};

const postEdge = (discr, parent, child) => {
  let messageSuccess = `Se ha creado correctamente la transición`;
  let messageError = `No se ha creado. `;
  return apiInstance
    .post(COMPONENT_URL.edge, {
      discr: discr,
      parent: parent,
      child: child
    })
    .then((response) => {
      setAlert(messageSuccess, 'success', 'state');
      return response;
    })
    .catch((error) => {
      let statusText = '';
      if (error.response.data && error.response.data.non_field_errors[0] === 'The fields parent, child must make a unique set.') {
        statusText = 'Ya existe la transición ';
      }
      messageError += statusText;
      setAlert(messageError, 'error', 'edge');
      return Promise.reject(error);
    });
};

const putEdge = (url, discr, parent, child) => {
  let messageSuccess = `Se ha editado correctamente.`;
  let messageError = `No se ha editado. `;
  return apiInstance
    .put(url, {
      discr: discr,
      parent: parent,
      child: child
    })
    .then((response) => {
      setAlert(messageSuccess, 'success', 'state');
      return response;
    })
    .catch((error) => {
      let statusText = '';
      if (error.response.data && error.response.data.non_field_errors[0] === 'The fields parent, child must make a unique set.') {
        statusText = 'Ya existe la transición ';
      }
      messageError += statusText;
      setAlert(messageError, 'error', 'edge');
      return Promise.reject(error);
    });
};

const deleteEdge = (url, name) => {
  let messageSuccess = `Se ha eliminado correctamente la transición `;
  let messageError = `No se ha eliminado. `;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, 'success', 'edge');
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, 'error', 'edge');
      return Promise.reject(error);
    });
};

export { getEdges, getAllEdges, getEdge, postEdge, putEdge, deleteEdge };
