import { isEmpty, validateAlphanumeric, validateEmail, validateLength, validateNumbers, validateSpace, validateURL } from "../validators";

const validateName = (name) => {
  //return (validateAlphanumeric(name) && validateLength(name, 100) && validateSpace(name))// tengo que ver la funcion de este metodo validateSpace(name)
  if(name){
    return (validateAlphanumeric(name) && validateLength(name, 100))
  }
  return null
}

const validateSelect = (option) => {
  if(option){
    return (!isEmpty(option))
  }
  return null
}

const validateContact = (contact) => {
  if (contact){
    return (validateSpace(contact))// no entinedo porque un selec
  }
  return null
}

const validateContactMail = (contactMail) => {
  return validateSpace(contactMail) && validateEmail(contactMail);
};

const validateContactPhone = (contactPhone) => {
  return validateSpace(contactPhone) && validateNumbers(contactPhone);
};

const validateContactURI = (contactURI) => {
  return validateSpace(contactURI) && validateURL(contactURI);
};

const validateContactTelegram = (contactTelegram) => {
  return validateSpace(contactTelegram) && validateAlphanumeric(contactTelegram);
};

export {
  validateName,
  validateSelect,
  validateContact,
  validateContactMail,
  validateContactPhone,
  validateContactURI,
  validateContactTelegram
};
