import  apiInstance  from "../api";
import { COMPONENT_URL , PAGE} from '../../config/constant';
import setAlert from '../../utils/setAlert';



const getMinifiedState = () => {//el parametro es para completar la url con el numero de pagina
    let messageError = `No se pudo recuperar la informacion de los estados`;
    return apiInstance.get(COMPONENT_URL.stateMinifiedList)
    .then(response => {        
        return response.data;
    }).catch( error => { 
        setAlert(messageError, "error", "state");
        return Promise.reject(error);
    });
}

const getStates = (currentPage, filters,order) => {//el parametro es para completar la url con el numero de pagina
    let messageError = `No se pudo recuperar la informacion de los estados`;
    return apiInstance.get(COMPONENT_URL.state+ PAGE+ currentPage+  '&ordering=' + order +'&' + filters)
    .then(response => {        
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "state");
        return Promise.reject(error);
    });
}

const getAllStates = (currentPage = 1, results = [], limit = 100) => {
            
    return apiInstance.get(COMPONENT_URL.state, { params: { page: currentPage, page_size: limit } })       
        .then((response) => {
            let res = [...results, ...response.data.results]                                    
            if(response.data.next !== null){                                
                return getAllStates(++currentPage, res, limit)
            }
            else{
                return res;     
            }                  
        })
        .catch((error) => {
            return Promise.reject(error);            
        })   

}

const postState = ( name,attended,solved,active,description,children) => {  
    let messageSuccess = `El estado ${name} se ha creado correctamente. `;
    let messageError = `El estado ${name} no se ha creado. `; 
    return apiInstance.post(COMPONENT_URL.state, {
        name: name,
        attended: attended,
        solved:solved,
        active:active,
        description:description,
        children:children 
    }).then(response => {
        setAlert(messageSuccess , "success", "state");
        return response;
    }).catch( error => { 

        let statusText = ""; 
        if (error.response.status === 400){
            console.log("status 400")
            if (error.response.data.attended && error.response.data.attended[0] === "Must be a valid boolean.") {
                statusText = "Debe ingresar un valor en el campo 'Atendido'.";
            } else if (error.response.data.solved && error.response.data.solved[0] === "Must be a valid boolean.") {
                statusText = "Debe ingresar un valor en el campo 'Resuelto'.";
            } else if (error.response.data.slug && error.response.data.slug[0].includes("Ya existe una entidad State con slug")) {
                statusText = "Ingrese un nombre diferente.";
                console.log("Error de slug");
            }
        }

        messageError += statusText;
        setAlert(messageError , "error", "state");
        return Promise.reject(error);
    });
}
const putState = ( url,name,attended,solved,active,description,children) => {
    let messageSuccess = `EL estado ${name} se pudo editar correctamente`;
    let messageError = `El estado ${name} no se pudo editar`;
    return apiInstance.put(url, {
        name: name,
        attended: attended,
        solved:solved,
        active:active,
        description:description,
        children:JSON.stringify(children)
        
    }).then(response => {
        setAlert(messageSuccess, "success", "state");
        return response;
    }).catch( error => { 

        let statusText = ""; 
        if (error.response.status === 400){
            console.log("status 400")
            if (error.response.data.attended && error.response.data.attended[0] === "Must be a valid boolean.") {
                statusText = "Debe ingresar un valor en el campo 'Atendido'.";
            } else if (error.response.data.solved && error.response.data.solved[0] === "Must be a valid boolean.") {
                statusText = "Debe ingresar un valor en el campo 'Resuelto'.";
            } else if (error.response.data.slug && error.response.data.slug[0].includes("Ya existe una entidad State con slug")) {
                statusText = "Ingrese un nombre diferente.";
            }
        }

        messageError += statusText;
        setAlert(messageError , "error", "state");
        return Promise.reject(error);
    });
}

const deleteState = (url, name) => {//

    let messageSuccess = `El estado ${name} se ha eliminado correctamente.`;
    let messageError = `El estado ${name} no se ha eliminado`;
    return apiInstance.delete(url).then(response => {
        setAlert(messageSuccess , "success", "state");
        return response;
    }).catch( error => { 
        let statusText = ""; 
        if(error.response.data.error && error.response.data.error[0].includes("Cannot delete some instances of model 'State' because they are referenced through protected foreign keys")){
            statusText = ", esta referenciado.";
        }
        messageError += statusText;
        setAlert(messageError , "error", "state");
        return Promise.reject(error);
    });
}

const isActive = (url, active) =>{
    let messageSuccess = !active ? `El estado ha sido desactivado` : `El estado ha sido activado`;
    let messageError = `El estado no se pudo modificar`;
    return apiInstance.patch(url, {
        active: active
    } ).then(response => {
        setAlert(messageSuccess , "success", "state");
        return response;
    }).catch( error => { 
        setAlert(messageError, "error", "state");
        return Promise.reject(error);
    });
}

const getState = (url) => { 
    let messageError = `No se pudo recuperar la informacion del estado`;
    return apiInstance.get(url)
    .then(response => {        
        return response;
    }).catch( error => { 
        setAlert(messageError , "error", "state");
        return Promise.reject(error);
    });
}

export { getStates, getAllStates, postState, putState, deleteState, isActive, getState, getMinifiedState }

