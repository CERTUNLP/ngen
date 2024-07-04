import  apiInstance  from "../api";
import { COMPONENT_URL } from '../../config/constant';
import setAlert from '../../utils/setAlert';

const getMinifiedTlp = () => {
    let messageError = `No se pudo recuperar la informacion de TLP`;
    return apiInstance.get(COMPONENT_URL.tlpMinifiedList)
    .then(response => {      
        return response.data;
    }).catch( error => { 
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const getTLP = (filters,order) => {//hay que agregar pagiandor en tlp
    let messageError = `No se pudo recuperar la informacion de TLP`;
    return apiInstance.get(COMPONENT_URL.tlp+ '?ordering=' + order +'&' + filters)
    .then(response => {   
        return response;
    }).catch( error => { 
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const getTLPSpecific = (url) => {
    return apiInstance.get(url);
}

export { getTLP, getTLPSpecific, getMinifiedTlp };