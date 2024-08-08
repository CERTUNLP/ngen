import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from '../../config/constant';
import setAlert from '../../utils/setAlert';
import i18next from "i18next";

const getMinifiedCase = () => {//el parametro es para completar la url con el numero de pagina
    let messageError = i18next.t('ngen.artifact.error');
    return apiInstance.get(COMPONENT_URL.caseMinifiedList)
        .then(response => {
            return response.data;
        }).catch(error => {
            setAlert(messageError, "error", "case");
            return Promise.reject(error);
        });
}

const getCases = (currentPage, filters, order) => { //+- id, date, attend_date, priority
    let messageError = i18next.t('ngen.cases.info.error') + " .";
    return apiInstance.get(COMPONENT_URL.case + PAGE + currentPage + '&ordering=' + order + '&' + filters)
        .then(response => {
            return response;
        }).catch(error => {
            let statusText = error.response.statusText;
            messageError += statusText;
            setAlert(messageError, "error", "case");
            return Promise.reject(error);
        });
}

const getCase = (url) => {
    let messageError = i18next.t('ngen.case.info.error') + " .";
    return apiInstance.get(url)
        .then(response => {
            return response;
        }).catch(error => {
            let statusText = error.response.statusText;
            messageError += statusText;
            setAlert(messageError, "error", "case");
            return Promise.reject(error);
        });
}

const getAllCases = (currentPage = 1, results = [], limit = 100) => {
    return apiInstance.get(COMPONENT_URL.case, { params: { page: currentPage } })//, page_size: limit
        .then((response) => {
            let res = [...results, ...response.data.results]
            if (response.data.next !== null) {
                return getAllCases(++currentPage, res, limit)
            }
            else {
                return res;
            }
        })
        .catch((error) => {
            return Promise.reject(error);
        })
}

const getOrderingCases = (currentPage = 1, results = [], limit = 100, id = '+id') => {
    return apiInstance.get(COMPONENT_URL.case, { params: { page: currentPage, ordering: id } })//, page_size: limit
        .then((response) => {
            let res = [...results, ...response.data.results]
            if (response.data.next !== null) {
                return getOrderingCases(++currentPage, res, limit, id)
            }
            else {
                return res;
            }
        })
        .catch((error) => {
            return Promise.reject(error);
        })
}
//const postCase = (date, lifecycle, parent, priority, tlp, assigned, state, comments, evidence, attend_date, solve_date) => {
const postCase = (formData) => {
    let messageSuccess = i18next.t('ngen.create.case.success'); 
    let messageError = i18next.t('ngen.create.case.error') + " .";
    return apiInstance.post(COMPONENT_URL.case, formData)
        .then(response => {
            setAlert(messageSuccess, "success", "case");
            return response;
        }).catch(error => {
            console.log(error.response.data)
            if (error.response.status === 400) {
                if (error.response.data.parent !== null) {
                    messageError += i18next.t('ngen.create.case.error.network') + " .";
                }
                else if (error.response.data.assigned !== null) {
                    messageError += i18next.t('ngen.create.case.error.user') + " .";
                }
            }
            setAlert(messageError, "error", "case");
            return Promise.reject(error);
        });
}

//const putCase = (url, date, lifecycle, parent, priority, tlp, assigned, state, comments, evidence, attend_date, solve_date) => {
const putCase = (url, formData) => {
    let messageSuccess = i18next.t('ngen.edit.case.success'); 
    let messageError = i18next.t('ngen.edit.case.error') + " .";
    return apiInstance.put(url, formData

    ).then(response => {
        setAlert(messageSuccess, "success", "case");
        return response;
    }).catch(error => {
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError, "error", "case");
        return Promise.reject(error);
    });
}
const patchCase = (url, events) => {
    let messageSuccess = i18next.t('ngen.edit.case.success'); 
    let messageError = i18next.t('ngen.edit.case.error') + " .";
    return apiInstance.patch(url,
        {
            events: events
        }
    ).then(response => {
        setAlert(messageSuccess, "success", "case");
        return response;
    }).catch(error => {

        let statusText = error.response.statusText;
        messageError += statusText;
        console.log(error.response.statusText)
        setAlert(messageError, "error", "case");
        return Promise.reject(error);
    });
}


const deleteCase = (url) => {
    let messageSuccess = i18next.t('ngen.delete.case.success'); 
    let messageError = i18next.t('ngen.delete.case.error') + " .";
    return apiInstance.delete(url)
        .then(response => {
            setAlert(messageSuccess, "success", "case");
            return response;
        }).catch(error => {
            let statusText = error.response.statusText;
            messageError += statusText;
            setAlert(messageError, "error", "case");
            return Promise.reject(error);
        });
}

const mergeCase = (urlParent, urlChildren) => {
    let messageSuccess = i18next.t('ngen.merge.case.success'); 
    let messageError = i18next.t('ngen.merge.case.error') + " .";
    return apiInstance.patch(urlChildren,
        {
            parent: urlParent
        }).then(response => {
            setAlert(messageSuccess, "success", "case");
            return response;
        }).catch(error => {
            let statusText = error.response.statusText;
            messageError += statusText;
            setAlert(messageError, "error", "case");
            return Promise.reject(error);
        });
}

export { getCases, getAllCases, getOrderingCases, getCase, postCase, putCase, deleteCase, mergeCase, patchCase, getMinifiedCase };
