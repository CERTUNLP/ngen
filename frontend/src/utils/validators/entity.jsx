import { isEmpty, validateAlphanumeric, validateLength } from "../validators";

const validateName = (name) => {
  //return (validateAlphanumeric(name) && validateLength(name, 100) && validateSpace(name)) no me queda en claro para que esta el validatespace
  return validateLength(name, 255) && !isEmpty(name);
};

export { validateName };
