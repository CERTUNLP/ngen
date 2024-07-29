import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from '../../config/constant';
import setAlert from '../../utils/setAlert';

const getEvents = (currentPage, filters, order) => {//el parametro es para completar la url con el numero de pagina
    return apiInstance.get(COMPONENT_URL.event + PAGE + currentPage + '&ordering=' + order + '&' + filters);
}
const postEvent = (formData) => {//el parametro es para completar la url con el numero de pagina
    let messageSuccess = `El evento se pudo crear correctamente`;
    let messageError = `El evento no se pudo crear`;

    return apiInstance.post(COMPONENT_URL.event, formData).then(response => {
        setAlert(messageSuccess, "success", "event");
        return response;
    }).catch(error => {

        setAlert(messageError, "error", "event");
        return Promise.reject(error);
    });
}
const putEvent = (url, formData) => {//el parametro es para completar la url con el numero de pagina
    let messageSuccess = `El evento se pudo editar correctamente`;
    let messageError = `El evento no se pudo editar`;

    return apiInstance.put(url, formData).then(response => {
        setAlert(messageSuccess, "success", "event");
        return response;
    }).catch(error => {
        console.log(error.response.data._detail)
        if (error.response.data._detail.includes("already exists")) {
            messageError += ". Se intenta cargar un archivo que ya existe"
            setAlert(messageError, "error", "event");
        }
        return Promise.reject(error);
    });
}

const patchEvent = (url, formData) => {//el parametro es para completar la url con el numero de pagina
    let messageSuccess = `El evento se pudo editar correctamente`;
    let messageError = `El evento no se pudo editar`;

    return apiInstance.patch(url, formData).then(response => {
        setAlert(messageSuccess, "success", "event");
        return response;
    }).catch(error => {
        setAlert(messageError, "error", "event");
        return Promise.reject(error);
    });
}

const getEvent = (url) => {//el parametro es para completar la url con el numero de pagina
    return apiInstance.get(url);
}

const deleteEvent = (url) => {
    let messageSuccess = `El evento se pudo eliminar correctamente`;
    let messageError = `El evento no se pudo eliminar`;
    return apiInstance.delete(url).then(response => {
        setAlert(messageSuccess, "success", "event");
        return response;
    }).catch(error => {
        setAlert(messageError, "error", "event");
        return Promise.reject(error);
    });
}
const mergeEvent = (urlParent, urlChildren) => {
    let messageSuccess = `Los eventos han sido mergeados correctamente.`;
    let messageError = `Los eventos no han sido mergeados. `;
    return apiInstance.patch(urlChildren,
        {
            parent: urlParent
        }).then(response => {
            setAlert(messageSuccess, "success", "event");
            return response;
        }).catch(error => {
            let statusText = error.response.statusText;
            messageError += statusText;
            setAlert(messageError, "error", "event");
            return Promise.reject(error);
        })
}
const getAllEvents = (currentPage = 1, results = [], limit = 100) => {
    return apiInstance.get(COMPONENT_URL.event, { params: { page: currentPage } })//, page_size: limit
        .then((response) => {
            let res = [...results, ...response.data.results]
            if (response.data.next !== null) {
                return getAllEvents(++currentPage, res, limit)
            }
            else {
                res.sort((p, q) => {
                    return p.slug > q.slug ? 1 : -1;
                });
                return res;
            }
        })
        .catch((error) => {
            return Promise.reject(error);
        })
}
const getListEvents = (list) => {
    const listEvents = []
    list.forEach(function (url) {
        apiInstance.get(url).then((response) => {
            listEvents.push(response.data)
        })
            .catch((error) => {
                return Promise.reject(error);
            })
    });
    return list
}

export { getEvents, postEvent, putEvent, deleteEvent, mergeEvent, getEvent, getAllEvents, getListEvents, patchEvent };
