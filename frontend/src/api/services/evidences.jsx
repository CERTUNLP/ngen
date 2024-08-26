import apiInstance from '../api';
import { COMPONENT_URL } from '../../config/constant';
import setAlert from '../../utils/setAlert';

const getEvidences = () => {
  return apiInstance.get(COMPONENT_URL.evidence);
};
const getEvidence = (url) => {
  return apiInstance.get(url);
};
const patchEvidence = (url, evidence) => {
  return apiInstance.patch(url, {
    evidence: evidence
  });
};
const deleteEvidence = (url) => {
  let messageSuccess = `La evidencia pudo eliminar correctamente`;
  //let messageError = `El evento no se pudo editar`;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, 'success', 'evidence');
      return response;
    })
    .catch((error) => {
      //console.log(error.response)
      //setAlert(messageError, "error", "case");
      return Promise.reject(error);
    });
};

export { getEvidences, getEvidence, patchEvidence, deleteEvidence };
