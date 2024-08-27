import { isBlank, isEmpty, isNull, validateAlphanumeric, validateLength } from "../validators";

const validateUnrequiredInput = (input) => {
  return !(isNull(input) || isBlank(input));
};
const validatePlaybookName = (name) => {
  return validateLength(name, 255) && !isEmpty(name);
};

export { validatePlaybookName, validateUnrequiredInput };
