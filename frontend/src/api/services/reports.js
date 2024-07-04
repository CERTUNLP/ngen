import apiInstance from "../api";
import setAlert from '../../utils/setAlert';
import { COMPONENT_URL, PAGE } from '../../config/constant';

const getReports = (currentPage, filters,order) => {
    let messageError = `No se ha recuperado la informacion del reporte. `;
    return apiInstance.get(COMPONENT_URL.report + PAGE + currentPage + '&ordering=' + order +'&' + filters)
    .then(response => {        
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "report");
        return Promise.reject(error);
    });
}
const getReport = (url) => {
    let messageError = `No se ha recuperado la informacion del reporte. `;
    return apiInstance.get(url)
    .then(response => {        
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "report");
        return Promise.reject(error);
    });
}
const getAllReports = (currentPage = 1, results = [], limit = 100) => {
    return apiInstance.get(COMPONENT_URL.report, { params: { page: currentPage } })//, page_size: limit
        .then((response) => {
            let res = [...results, ...response.data.results]                                    
            if(response.data.next !== null){                                
                return getAllReports(++currentPage, res, limit)
            }
            else{
                return res;
            }                  
        })
        .catch((error) => {
            return Promise.reject(error);            
        })   
}

const postReport = (problem, derived_problem, verification, recommendations, more_information, lang, taxonomy)=>{
    let messageSuccess = `El reporte se ha creado correctamente.`;
    let messageError = `El reporte no se pudo crear. `;
    return apiInstance.post(COMPONENT_URL.report, {
        problem: problem,
        derived_problem: derived_problem,
        verification: verification,
        recommendations: recommendations,
        more_information: more_information,
        lang: lang,
        taxonomy: taxonomy
    }).then(response => {
        setAlert(messageSuccess, "success", "report");
        return response;
    }).catch( error => { 
        let statusText = ""; 
        if (error.response.status === 400){
            if (error.response.data.non_field_errors && error.response.data.non_field_errors[0] === "The fields lang, taxonomy must make a unique set.") {
                statusText = "Ya existe para esa taxonomia en ese idioma.";
            }  
        }
        messageError += statusText;
        setAlert(messageError , "error", "report");
        return Promise.reject(error);
    });
}

const putReport = (url, problem, derived_problem, verification, recommendations, more_information, lang, taxonomy) => {
    let messageSuccess = `El reporte se ha editado correctamente.`;
    let messageError = `El reporte no se ha editado. `;
    return apiInstance.put(url, 
        {
            problem: problem,
            derived_problem: derived_problem,
            verification: verification,
            recommendations: recommendations,
            more_information: more_information,
            lang: lang,
            taxonomy: taxonomy
        }).then(response => {
        setAlert(messageSuccess , "success", "report");
        return response;
    }).catch( error => { 
        let statusText = ""; 
        if (error.response.status === 400){
            if (error.response.data.non_field_errors && error.response.data.non_field_errors[0] === "The fields lang, taxonomy must make a unique set.") {
                statusText = "ya existe esa taxonomia con ese idioma ";
            }
        }
        messageError += statusText;
        setAlert(messageError , "error", "report");
        return Promise.reject(error);
    });
}


const deleteReport = (url) => {
    let messageSuccess = `El reporte se ha eliminado correctamente.`;
    let messageError = `El reporte no se ha eliminado. `;
    return apiInstance.delete(url)
    .then(response => {
        setAlert(messageSuccess , "success", "report");
        return response;
    }).catch( error => { 
        let statusText = error.response.statusText;
        messageError += statusText;
        setAlert(messageError , "error", "report");
        return Promise.reject(error);
    });
}

export { getReports, getAllReports, getReport, postReport, putReport, deleteReport };