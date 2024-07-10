import apiInstance from "../api";
import { COMPONENT_URL } from '../../config/constant';
import setAlert from '../../utils/setAlert';

const getProfile = () => {
    let messageError = `No se ha recuperado la informacion del usuario. `;
    return apiInstance.get(COMPONENT_URL.profile)
        .then(response => {
            return response;
        }).catch(error => {
            let statusText = error.response.statusText;
            messageError += statusText;
            setAlert(messageError, "error", "report");
            return Promise.reject(error);
        });
}

export { getProfile }
