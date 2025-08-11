import apiInstance from "../api";
import { COMPONENT_URL, PAGE } from "config/constant";
import setAlert from "utils/setAlert";

const getContactChecks = (currentPage, filters, order) => {
    let messageError = `No se pudo recuperar la información de los contact checks`;
    return apiInstance
        .get(COMPONENT_URL.contactCheck + PAGE + currentPage + "&ordering=" + order + "&" + filters)
        .then((response) => {
            return response;
        })
        .catch((error) => {
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const getContactCheck = (url) => {
    let messageError = `No se pudo recuperar la información del contact check`;
    return apiInstance
        .get(url)
        .then((response) => {
            return response;
        })
        .catch((error) => {
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};


const getAllContactChecks = (currentPage = 1, results = [], limit = 100) => {
    return apiInstance
        .get(COMPONENT_URL.contactCheck, {
            params: {
                page: currentPage,
                page_size: limit
            }
        })
        .then((response) => {
            let res = [...results, ...response.data.results];
            if (response.data.next !== null) {
                return getAllContactChecks(++currentPage, res, limit);
            } else {
                return res;
            }
        })
        .catch((error) => {
            return Promise.reject(error, "contactcheck");
        });
};

const postContactCheck = (name, type, value, description) => {
    let messageSuccess = `El contact check ${name} se pudo crear correctamente. `;
    let messageError = `El contact check ${name} no se pudo crear. `;
    return apiInstance
        .post(COMPONENT_URL.contactCheck, {
            name,
            type,
            value,
            description
        })
        .then((response) => {
            setAlert(messageSuccess, "success", "contactcheck");
            return response;
        })
        .catch((error) => {
            let statusText = "";

            if (error.response && error.response.status === 400) {
                if (error.response.data.name && error.response.data.name[0].includes("ya existe")) {
                    statusText = "Ingrese un nombre diferente. ";
                }
            } else if (error.message === "Cannot read properties of undefined (reading 'code')") {
                messageError = `El contact check ${name} no puede ser creado porque el servidor no responde`;
            } else if (error.response) {
                statusText = error.response.statusText;
            }
            messageError += statusText;
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const putContactCheck = (url, name, type, value, description) => {
    let messageSuccess = `El contact check ${name} se pudo actualizar correctamente. `;
    let messageError = `El contact check ${name} no se pudo actualizar. `;
    return apiInstance
        .put(url, {
            name,
            type,
            value,
            description
        })
        .then((response) => {
            setAlert(messageSuccess, "success", "contactcheck");
            return response;
        })
        .catch((error) => {
            let statusText = "";
            if (error.response && error.response.status === 400) {
                if (error.response.data.name && error.response.data.name[0].includes("ya existe")) {
                    statusText = "Ingrese un nombre diferente. ";
                }
            } else if (error.message === "Cannot read properties of undefined (reading 'code')") {
                messageError = `El contact check ${name} no puede ser actualizado porque el servidor no responde`;
            } else if (error.response) {
                statusText = error.response.statusText;
            }
            messageError += statusText;
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const deleteContactCheck = (url) => {
    let messageSuccess = `El contact check se pudo eliminar correctamente. `;
    let messageError = `El contact check no se pudo eliminar`;
    return apiInstance
        .delete(url)
        .then((response) => {
            setAlert(messageSuccess, "success", "contactcheck");
            return response;
        })
        .catch((error) => {
            let statusText = "";
            if (
                error.response &&
                error.response.data.error &&
                error.response.data.error[0].includes(
                    "Cannot delete some instances of model 'ContactCheck' because they are referenced through protected foreign keys"
                )
            ) {
                statusText = ", está referenciado.";
            }
            messageError += statusText;
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const resendContactCheck = (contactcheck_uuid) => {
    let messageSuccess = `El contact check se reenvió correctamente. `;
    let messageError = `El contact check no se pudo reenviar`;
    return apiInstance
        .post(`/contactcheck/resend/${contactcheck_uuid}/`)
        .then((response) => {
            setAlert(messageSuccess, "success", "contactcheck");
            return response;
        })
        .catch((error) => {
            let statusText = "";
            if (error.response && error.response.status === 404) {
                statusText = "No existe el contact check.";
            } else if (error.message === "Cannot read properties of undefined (reading 'code')") {
                messageError = `El contact check no puede ser reenviado porque el servidor no responde`;
            } else if (error.response) {
                statusText = error.response.statusText;
            }
            messageError += statusText;
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const resendContactCheckByContactId = (contact_id) => {
    let messageSuccess = `El contact check se reenvió correctamente. `;
    let messageError = `El contact check no se pudo reenviar`;
    return apiInstance
        .post(`/contactcheck/contact/${contact_id}/send/`)
        .then((response) => {
            setAlert(messageSuccess, "success", "contactcheck");
            return response;
        })
        .catch((error) => {
            let statusText = "";
            if (error.response && error.response.status === 404) {
                statusText = "No existe el contact check.";
            } else if (error.message === "Cannot read properties of undefined (reading 'code')") {
                messageError = `El contact check no puede ser reenviado porque el servidor no responde`;
            } else if (error.response) {
                statusText = error.response.statusText;
            }
            messageError += statusText;
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const getContactCheckByContactId = (contact_id) => {
    let messageError = `No se pudo recuperar la información del contacto`;
    return apiInstance
        .get(`/contactcheck/contact/${contact_id}/`)
        .then((response) => {
            return response;
        })
        .catch((error) => {
            // setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

const setContactCheckConfirmed = (contactCheck) => {
    let messageSuccess = `El contact check se actualizó correctamente. `;
    let messageError = `El contact check no se pudo actualizar. `;
    return apiInstance
        .post(`/contactcheck/confirm/${contactCheck.uuid}/`, {
            confirmed: true,
        })
        .then((response) => {
            setAlert(messageSuccess, "success", "contactcheck");
            return response;
        })
        .catch((error) => {
            let statusText = "";
            if (error.response && error.response.status === 400) {
                if (error.response.data.confirmed && error.response.data.confirmed[0].includes("ya existe")) {
                    statusText = "Ingrese un estado diferente. ";
                }
            } else if (error.message === "Cannot read properties of undefined (reading 'code')") {
                messageError = `El contact check no puede ser actualizado porque el servidor no responde`;
            } else if (error.response) {
                statusText = error.response.statusText;
            }
            messageError += statusText;
            setAlert(messageError, "error", "contactcheck");
            return Promise.reject(error);
        });
};

export {
    getContactChecks,
    getAllContactChecks,
    getContactCheck,
    postContactCheck,
    deleteContactCheck,
    putContactCheck,
    resendContactCheck,
    resendContactCheckByContactId,
    getContactCheckByContactId,
    setContactCheckConfirmed,
};
