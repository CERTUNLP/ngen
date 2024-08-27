import { isBlank, isEmpty, validateFieldText, validateLength } from "../validators";

const validateName = (name) => {
  //return (validateFieldText(name) && validateLength(name, 100) && !isEmpty(name))
  return validateLength(name, 255) && !isEmpty(name);
};

const validateDescription = (description) => {
  return validateLength(description, 1000);
};

const validateSelect = (option) => {
  return !isEmpty(option);
};

const validateUnrequiredInput = (input) => {
  return !isBlank(input);
};

export { validateName, validateDescription, validateSelect, validateUnrequiredInput };
