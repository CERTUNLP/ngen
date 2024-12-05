import apiInstance from "../api";
import setAlert from "../../utils/setAlert";
import { COMPONENT_URL, PAGE } from "../../config/constant";

const getContacts = (currentPage, filters, order, asNetworkAdmin) => {
  let messageError = `No se ha recuperado la informacion de contactos. `;
  let component = asNetworkAdmin ? COMPONENT_URL.networkadminContact : COMPONENT_URL.contact;
  return apiInstance
    .get(component + PAGE + currentPage + "&ordering=" + order + "&" + filters)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "contact");
      return Promise.reject(error);
    });
};

const getContact = (url, avoidRaise = false) => {
  let messageError = `No se ha recuperado la informacion del contacto. `;
  return apiInstance
    .get(url)
    .then((response) => {
      return response;
    })
    .catch((error) => {
      if (avoidRaise) {
        return Promise.reject(error);
      }
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "contact");
      return Promise.reject(error);
    });
};

const getAllContacts = (currentPage = 1, results = [], limit = 100) => {
  return apiInstance
    .get(COMPONENT_URL.contact, { params: { page: currentPage } }) //, page_size: limit
    .then((response) => {
      let res = [...results, ...response.data.results];
      if (response.data.next !== null) {
        return getAllContacts(++currentPage, res, limit);
      } else {
        return res;
      }
    })
    .catch((error) => {
      return Promise.reject(error);
    });
};

const postContact = (name, username, public_key, type, role, priority, user, networks) => {
  let messageSuccess = `El contacto ${name} se ha creado correctamente.`;
  let messageError = `El contacto ${name} no se ha creado. `;
  return apiInstance
    .post(COMPONENT_URL.contact, {
      name: name,
      username: username,
      public_key: public_key,
      type: type,
      role: role,
      priority: priority,
      user: user,
      networks: networks
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "contact");
      return response;
    })
    .catch((error) => {
      let statusText = "";
      console.log(error.response.data.username[0]);
      if (error.response.data.username[0] !== null) {
        if (error.response.data.username[0] === "contact with this username already exists.") {
          statusText = " El contacto ya existe";
        }
      }
      messageError += statusText;
      setAlert(messageError, "error", "contact");
      return Promise.reject(error);
    });
};

const putContact = (url, name, username, public_key, type, role, priority, user) => {
  let messageSuccess = `El contacto ${name} se ha editado correctamente.`;
  let messageError = `El contacto ${name} no se ha editado. `;
  return apiInstance
    .put(url, {
      name: name,
      username: username,
      public_key: public_key,
      type: type,
      role: role,
      priority: priority,
      user: user
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "contact");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "contact");
      return Promise.reject(error);
    });
};

const patchContact = (url, name, username, public_key, type, role, priority, user) => {
  let messageSuccess = `El contacto ${name} se ha editado correctamente.`;
  let messageError = `El contacto ${name} no se ha editado. `;
  return apiInstance
    .patch(url, {
      name: name,
      username: username,
      public_key: public_key,
      type: type,
      role: role,
      priority: priority,
      user: user
    })
    .then((response) => {
      setAlert(messageSuccess, "success", "contact");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "contact");
      return Promise.reject(error);
    });
};

const deleteContact = (url, name) => {
  let messageSuccess = `El contacto ${name} se ha eliminado correctamente.`;
  let messageError = `El contacto ${name} no se ha eliminado. `;
  return apiInstance
    .delete(url)
    .then((response) => {
      setAlert(messageSuccess, "success", "contact");
      return response;
    })
    .catch((error) => {
      let statusText = error.response.statusText;
      messageError += statusText;
      setAlert(messageError, "error", "contact");
      return Promise.reject(error);
    });
};

const getMinifiedContact = () => {
  let messageError = `No se pudo recuperar la informacion del contacto`;
  return apiInstance
    .get(COMPONENT_URL.contactMinifiedList)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      setAlert(messageError, "error", "case");
      return Promise.reject(error);
    });
};

export { getContacts, getAllContacts, getContact, postContact, putContact, patchContact, deleteContact, getMinifiedContact };
