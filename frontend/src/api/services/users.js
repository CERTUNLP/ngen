import  apiInstance  from "../api";
import { COMPONENT_URL, PAGE } from '../../config/constant';
import setAlert from '../../utils/setAlert';

const getMinifiedUser = () => {//el parametro es para completar la url con el numero de pagina
    let messageError = `No se pudo recuperar la informacion de los usuarios`;
    return apiInstance.get(COMPONENT_URL.userMinifiedList)
    .then(response => {        
        return response.data;
    }).catch( error => { 
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}
const getUsers = (currentPage, filters,order) => {//el parametro es para completar la url con el numero de pagina
    let messageError = `No se pudo recuperar la informacion de los usuarios`;
    return apiInstance.get(COMPONENT_URL.user + PAGE + currentPage + '&ordering=' + order +'&' + filters)
    .then(response => {        
        return response;
    }).catch( error => { 
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const getUser = (url) => { 
    let messageError = `No se pudo recuperar la informacion del usuario`;
    return apiInstance.get(url).then(response => {        
        return response;
    }).catch( error => { 
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const getAllUsers = (currentPage = 1, results = [], limit = 100) => {
            
    return apiInstance.get(COMPONENT_URL.user, { params: { page: currentPage, page_size: limit } })       
        .then((response) => {
            console.log(response)
            let res = [...results, ...response.data.results]                                    
            if(response.data.next !== null){                                
                return getAllUsers(++currentPage, res, limit)
            }
            else{
                return res;     
            }                  
        })
        .catch((error) => {
            return Promise.reject(error);            
        })   

}

const postUser = (username, first_name, last_name, email, priority, is_active, password) => {
    let messageSuccess = `El usuario ${username} se pudo crear correctamente`;
    let messageError = `El usuario ${username} no se pudo crear`;
    
    return apiInstance.post(COMPONENT_URL.user, {
        username: username, 
        first_name: first_name, 
        last_name: last_name, 
        email: email, 
        priority: priority,
        is_active: is_active,
        password: password
    }).then(response => {
        setAlert(messageSuccess, "success");
        return response;
    }).catch( error => { 
        console.log(error.response)
        if (error.response.status === 400){
            //se informa que existe el username con ese nombre
            if(error.response.data.username === "A user with that username already exists." ){
                messageError = `El usuario ${username} se pudo crear correctamente porque ya existe en el sistema`;   
            }
        }else if(error.message === "Cannot read properties of undefined (reading 'code')"){
            //el backend o servidor no funciona
            messageError = `El usuario ${username} no puede ser creado porque el servidor no responde`;
        }
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const putUser = ( url,username, first_name, last_name, email, priority, is_active) => {
    let messageSuccess = `El usuario ${username} se pudo editar correctamente`;
    let messageError = `El usuario ${username} no se pudo editar`;
    return apiInstance.put(url, {
        username: username, 
        first_name: first_name, 
        last_name: last_name, 
        email: email, 
        priority: priority,
        is_active: is_active
    }).then(response => {
        setAlert(messageSuccess , "success");
        return response;
    }).catch( error => { 
        if (error.response.status === 400){
            //se informa que existe el username con ese nombre
            if(error.response.data.username === "A user with that username already exists." ){
                messageError = `El usuario ${username} se pudo edita correctamente porque ya existe en el sistema`;   
            }
        }else if(error.message === "Cannot read properties of undefined (reading 'code')"){
            //el backend o servidor no funciona
            messageError = `El usuario ${username} no puede ser editado porque el servidor no responde`;
        }
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const isActive = (url, active) => {
    let messageSuccess = !active ? `El usuario ha sido desactivado` : `El usuario ha sido activado`;
    let messageError = `El usuario no se pudo modificar`;
    return apiInstance.patch(url, {
        is_active: active
    } ).then(response => {
        setAlert(messageSuccess , "success");
        return response;
    }).catch( error => { 
        if(error.message === "Cannot read properties of undefined (reading 'code')"){
            //el backend o servidor no funciona
            messageError = !active ? `El usuario no pudo ser desactivado no pudo ser` : `El usuario no pudo ser activado no pudo ser`;
            setAlert(messageError, "error");

        }
        setAlert(messageError, "error");
        return Promise.reject(error);
    });
}

const deleteUser = (url) => {
    let messageSuccess = `El usuario se ha eliminado correctamente.`;
    let messageError = `EL usuario no se ha eliminado`;
    return apiInstance.delete(url).then(response => {
        setAlert(messageSuccess , "success");
        return response;
    }).catch( error => { 
        let statusText = ""; 
        if(error.response.data.error && error.response.data.error[0].includes("Cannot delete some instances of model 'User' because they are referenced through protected foreign keys")){
            statusText = ", esta referenciado.";
        } else if(error.message === "Cannot read properties of undefined (reading 'code')"){
            //el backend o servidor no funciona
            statusText = `. El servidor no responde.`;
        }
        messageError += statusText;
        setAlert(messageError, "error");
        
        
        return Promise.reject(error);
    })
}
/*
"error": [
        "(\"Cannot delete some instances of model 'User' because they are referenced through protected foreign keys: 
        'Case.user_creator', 'Case.assigned', 'Event.reporter'.\", {<Case: 1>, <Event: 1:unlp.com>})"
    ]
*/
export { getUsers, getUser, getAllUsers, postUser, putUser, deleteUser, isActive, getMinifiedUser};
