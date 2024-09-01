import { isBlank, isEmpty, validateFieldText, validateLength } from "../validators";

const validateName = (name) => {
  //return (validateFieldText(name) && validateLength(name, 100) && !isEmpty(name)) ver para que sirve  el isEmpty(name)
  return validateLength(name, 255) && !isEmpty(name);
};

const validateDescription = (description) => {
  return validateLength(description, 1000);
};

const validateType = (type) => {
  return !isEmpty(type);
};

const validateUnrequiredInput = (input) => {
  return !isBlank(input);
};

export { validateName, validateDescription, validateType, validateUnrequiredInput };
