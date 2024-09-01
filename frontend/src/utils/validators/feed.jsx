import { isBlank, isEmpty, validateFieldText, validateLength } from "../validators";

const validateName = (name) => {
  return validateLength(name, 255) && !isEmpty(name);
};

const validateDescription = (description) => {
  return validateLength(description, 255);
};

const validateUnrequiredInput = (input) => {
  return !isBlank(input);
};

export { validateName, validateDescription, validateUnrequiredInput };
