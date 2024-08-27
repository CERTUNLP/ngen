import { isBlank, isEmpty, isNull, validateAlphanumeric, validateLength } from "../validators";

const validateUnrequiredInput = (input) => {
  return !(isNull(input) || isBlank(input));
};
const validateTaskName = (name) => {
  return validateLength(name, 250) && !isEmpty(name);
};
const validateTaskDescription = (description) => {
  return validateLength(description, 1000);
};

export { validateTaskDescription, validateTaskName, validateUnrequiredInput };
