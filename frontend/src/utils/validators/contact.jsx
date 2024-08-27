import { isEmpty, validateAlphanumeric, validateEmail, validateLength, validateNumbers, validateSpace, validateURL } from "../validators";

const validateName = (name) => {
  return validateLength(name, 255) && !isEmpty(name);
};

const validateSelect = (option) => {
  return !isEmpty(option);
};

const validateContact = (contact) => {
  return validateSpace(contact); // no entinedo porque un selec
};

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
