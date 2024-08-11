import apiInstance from "../api";
import { COMPONENT_URL } from '../../config/constant';
import setAlert from '../../utils/setAlert';


const getMinifiedTaxonomyGroups = () => {
  let messageError = `No se pudo recuperar la informacion de los grupos de taxonomias`;
  return apiInstance.get(COMPONENT_URL.taxonomyGroupMinifiedList).then(response => {
    return response.data;
  }).catch(error => {
    setAlert(messageError, "error", "taxonomy group");
    return Promise.reject(error);
  });
}

export { getMinifiedTaxonomyGroups }
