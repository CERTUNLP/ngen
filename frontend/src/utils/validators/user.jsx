import { isBlank, isEmpty, validateEmail, validateFieldText, validateLength, validateUsername } from "../validators";

const validateUserName = (name) => {
  return validateUsername(name) && validateLength(name, 150);
};

const validateName = (name) => {
  return validateFieldText(name) && validateLength(name, 255) && !isEmpty(name);
};

const validateUserMail = (mail) => {
  return validateEmail(mail) && validateLength(mail, 255) && !isEmpty(mail);
};

const validateSelect = (option) => {
  return !isEmpty(option);
};

const validatePassword = (password, passwordConfirmation) => {
  return !isBlank(password) && password === passwordConfirmation;
};

const getPasswordErrors = (password, personalInfo = {}) => {
  const errors = [];
  if (!password) return errors;

  if (password.length < 8) {
    errors.push("password.too_short");
  }
  if (/^\d+$/.test(password)) {
    errors.push("password.entirely_numeric");
  }
  const infoFields = [
    personalInfo.username,
    personalInfo.email,
    personalInfo.first_name,
    personalInfo.last_name,
  ].filter(Boolean);
  for (const field of infoFields) {
    const parts = field.toLowerCase().split(/[@._\-\s]+/);
    for (const part of parts) {
      if (part.length > 2 && password.toLowerCase().includes(part)) {
        errors.push("password.similar");
        break;
      }
    }
    if (errors.includes("password.similar")) break;
  }

  return errors;
};

const validateUnrequiredInput = (input) => {
  return !isBlank(input);
};

export {
  validateUserName,
  validateName,
  validateUserMail,
  validateSelect,
  validatePassword,
  getPasswordErrors,
  validateUnrequiredInput,
};
