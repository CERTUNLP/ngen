import apiInstance from "../api";
import setAlert from '../../utils/setAlert';
import { COMPONENT_URL, PAGE } from '../../config/constant';

const getTemplates = (currentPage, filters,order) => {
  let messageError = `No se pudo recuperar la informacion de las plantillas`;
  return apiInstance.get(COMPONENT_URL.template + PAGE + currentPage + '&ordering=' + order +'&' + filters)
  .then(response => {        
    return response;
}).catch( error => { 
    setAlert(messageError, "error", "template");
    return Promise.reject(error);
});
}

const createCases = (url) => { 
  let messageError = `No se pudo recuperar la  plantilla`;
  return apiInstance.get(url+"create-cases/").then(response => {        
      return response;
  }).catch( error => { 
      setAlert(messageError, "error", "template");
      return Promise.reject(error);
  });
}

const getTemplate = (url) => { 
  let messageError = `No se pudo recuperar la  plantilla`;
  return apiInstance.get(url).then(response => {        
      return response;
  }).catch( error => { 
      setAlert(messageError, "error", "template");
      return Promise.reject(error);
  });
}

const postTemplate = (address_value,active,priority,event_taxonomy,event_feed,case_lifecycle,case_tlp,case_state) => {
  let messageSuccess = `La plantilla se pudo crear correctamente`;
  let messageError = `La plantilla no se pudo crear`;
  const body = {
    address_value: address_value,
    active: active,
    priority: priority,
    event_taxonomy: event_taxonomy,
    event_feed: event_feed,
    case_lifecycle: case_lifecycle,
    case_tlp: case_tlp,
    case_state: case_state
  } 
  return apiInstance.post(COMPONENT_URL.template, body).then(response => {
    
    setAlert(messageSuccess, "success", "template");
    return response;
}).catch( error => { 
  console.log(error)
  //
    if (error.response.status === 400 ) { 
      if(error.response.data.__all__[0] === "CIDR, Domain, Taxonomy, Feed tuple must be unique") {
            messageError += '. Ya existe una plantilla para eventos con esas caracteristicas ';
        }
    } 
    setAlert(messageError, "error", "template");
    return Promise.reject(error);
});
}

const putTemplate = ( url, address_value,active,priority,event_taxonomy,event_feed,case_lifecycle,case_tlp,case_state) => {
  let messageSuccess = `La plantilla se pudo editar correctamente`;
    let messageError = `La plantilla no se pudo editar`;
  return apiInstance.put(url, {
    address_value: address_value,
    active: active,
    priority: priority,
    event_taxonomy: event_taxonomy,
    event_feed: event_feed,
    case_lifecycle: case_lifecycle,
    case_tlp: case_tlp,
    case_state: case_state
  }).then(response => {
    setAlert(messageSuccess , "success", "template");
    return response;
}).catch( error => { 
    setAlert(messageError, "error", "template");
    return Promise.reject(error);
});
}

const deleteTemplate = (url) => {
  let messageSuccess = `La plantilla se pudo eliminar correctamente`;
  let messageError = `La plantilla no se pudo eliminar`;
  return apiInstance.delete(url).then(response => {
    setAlert(messageSuccess , "success", "template");
    return response;
}).catch( error => { 
    setAlert(messageError, "error", "template");
    return Promise.reject(error);
})
}

const getAllTemplate = (currentPage = 1, results = [], limit = 100) => {
            
  return apiInstance.get(COMPONENT_URL.template, { params: { page: currentPage, page_size: limit } })       
      .then((response) => {
          let res = [...results, ...response.data.results]                                    
          if(response.data.next !== null){                                
              return getAllTemplate(++currentPage, res, limit)
          }
          else{
              return res;     
          }                  
      })
      .catch((error) => {
          return Promise.reject(error);            
      })   

}

const isActive = (url, active) =>{
  let messageSuccess = !active ? `La plantilla ha sido desactivado` : `La plantilla ha sido activado`;
  let messageError = `La plantilla no se pudo modificar`;
  return apiInstance.patch(url, {
      active: active
  } ).then(response => {
    setAlert(messageSuccess , "success", "template");
    return response;
}).catch( error => { 
    setAlert(messageError, "error", "template");
    return Promise.reject(error);
});
}

export  {getTemplates, getTemplate, postTemplate, putTemplate, deleteTemplate, isActive, getAllTemplate, createCases}