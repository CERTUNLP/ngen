import  apiInstance  from "../api";
import { COMPONENT_URL, PAGE } from '../../config/constant';
import setAlert from '../../utils/setAlert';

const getMinifiedFeed = () => { //+- id, name, slug, created, modified
    let messageError = `No se pudo recuperar la informacion de las fuentes de informacion`;
    return apiInstance.get(COMPONENT_URL.feedMinifiedList )
    .then(response => {        
        return response.data;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}

const getFeeds = (currentPage, filters,order) => { //+- id, name, slug, created, modified
    let messageError = `No se pudo recuperar la informacion de las fuentes de informacion`;
    return apiInstance.get(COMPONENT_URL.feed + PAGE + currentPage + '&ordering=' + order +'&' + filters )
    .then(response => {        
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}

const getFeed = (url) => {
    let messageError = `No se pudo recuperar la informacion de la fuente de informacion`;
    return apiInstance.get(url)
    .then(response => {        
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}

const getAllFeeds = (currentPage = 1, results = [], limit = 100) => {
    let messageError = `No se pudo recuperar la informacion de las fuentes de informacion`;            
    return apiInstance.get(COMPONENT_URL.feed, { params: { page: currentPage, page_size: limit } })       
        .then((response) => {
            console.log(response)
            let res = [...results, ...response.data.results]                                    
            if(response.data.next !== null){                                
                return getAllFeeds(++currentPage, res, limit)
            }
            else{
                return res;     
            }                  
        })
        .catch((error) => {
            setAlert(messageError, "error", "feed");
            return Promise.reject(error);            
        })   

}

const postFeed = (name, description, active) => {
    let messageSuccess = `La fuente de informacion ${name} se pudo crear correctamente`;
    let messageError = `La fuente de informacion ${name} no se pudo crear`;
    return apiInstance.post(COMPONENT_URL.feed, {
        name: name, 
        description: description,
        active: active
    }).then(response => {
        setAlert(messageSuccess, "success", "feed");
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}


const putFeed = (url, name, description, active) => {
    let messageSuccess = `La fuente de informacion ${name} se pudo editar correctamente`;
    let messageError = `La fuente de informacion ${name} no se pudo editar`;
    return apiInstance.put(url, {
        name: name, 
        description: description,
        active: active
    }).then(response => {
        setAlert(messageSuccess , "success", "feed");
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}


const putActivationStatus= (url, state, name) => {
    let messageSuccess = !state ? `La fuente de informacion ${name} ha sido desactivada` : `La fuente de informacion ${name} ha sido activada`;
    let messageError = `La fuente de informacion ${name} no se pudo modificar`;
    return apiInstance.patch(url, {
        active: state
    }).then(response => {
        setAlert(messageSuccess , "success", "feed");
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}


const deleteFeed = (url, name) => {
    let messageSuccess = `La fuente de informacion ${name} se pudo eliminar correctamente`;
    let messageError = `La fuente de informacion ${name} no se pudo eliminar`;
    return apiInstance.delete(url).then(response => {
        setAlert(messageSuccess , "success", "feed");
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "feed");
        return Promise.reject(error);
    });
}


export { getFeeds, getFeed, getAllFeeds, postFeed, putFeed, putActivationStatus, deleteFeed, getMinifiedFeed };