import apiInstance from "../api";
import setAlert from '../../utils/setAlert';
import { COMPONENT_URL, PAGE } from '../../config/constant';

const getNetworks = (currentPage, filters,order) => {
    let messageError = `No se ha recuperado la informacion de redes. `;
    return apiInstance.get(COMPONENT_URL.network + PAGE + currentPage + '&ordering=' + order +'&' + filters)
    .then(response => {        
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        console.log(error.response.statusText)
        messageError += statusText;
        setAlert(messageError , "error", "network");
        return Promise.reject(error);
    });
}
const getNetwork = (url) => {
    let messageError = `No se ha recuperado la informacion de la red. `;
    return apiInstance.get(url)
    .then(response => {        
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "network");
        return Promise.reject(error);
    });
}
const getAllNetworks = (currentPage = 1, results = [], limit = 100) => {
    return apiInstance.get(COMPONENT_URL.network, { params: { page: currentPage } })//, page_size: limit
        .then((response) => {
            let res = [...results, ...response.data.results]                                    
            if(response.data.next !== null){                                
                return getAllNetworks(++currentPage, res, limit)
            }
            else{
                return res;
            }                  
        })
        .catch((error) => {
            return Promise.reject(error);            
        })   
}

const postNetwork = (children, active, type, parent, network_entity, contacts, address_value) => {
    let messageSuccess = `La red ${address_value} se ha creado correctamente.`;
    let messageError 
    return apiInstance.post(COMPONENT_URL.network, {        
        children: children,
        address_value: address_value,
        active: active,
        type: type,
        parent: parent,
        network_entity: network_entity,
        contacts: contacts //*
    }).then(response => {
        setAlert(messageSuccess, "success", "network");
        return response;
    }).catch( error => { 
         if (error.response.status === 400 ) { 
            if(error.response.data.domain[0] === "Already exists a network with this domain") {
                messageError = 'El cidr o dominio ya existe ';
            }
        } 
        setAlert(messageError , "error", "network");
        return Promise.reject(error);
    });
}

const putNetwork = (url, children, active, type, parent, network_entity, contacts, address_value) => {
    let messageSuccess = `La red ${address_value} se ha editado correctamente.`;
    let messageError = `La red ${address_value} no se ha editado. `;
    return apiInstance.put(url, 
    {
        children: children,
        address_value:address_value,
        active: active, //*
        type: type, //*
        parent: parent,
        network_entity: network_entity,
        contacts: contacts //*
    }).then(response => {
        setAlert(messageSuccess , "success", "network");
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "network");
        return Promise.reject(error);
    });
}


const deleteNetwork = (url, name) => {
    let messageSuccess = `La red ${name} se ha eliminado correctamente.`;
    let messageError = `La red ${name} no se ha eliminado. `;
    return apiInstance.delete(url)
    .then(response => {
        setAlert(messageSuccess , "success", "network");
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "network");
        return Promise.reject(error);
    });
}

const isActive = (url, active, name) => { 
    let messageSuccess = !active ? `La red ${name} ha sido desactivada.` : `La red ${name} ha sido activada.`;
    let messageError = !active ? `La red ${name} no ha sido desactivada. ` : `La red ${name} no ha sido activada. `;
    return apiInstance.patch(url, {
        active: active
    }).then(response => {
        setAlert(messageSuccess , "success", "network");
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "network");
        return Promise.reject(error);
    });
}

export { getNetworks, getAllNetworks, getNetwork, postNetwork, putNetwork, deleteNetwork, isActive };
