import { isBlank, isEmpty, isNull, validateCidr, validateLength, validateSpace, validateSpaces, validateURL } from "../validators";

const validateSelect = (option) => {
  return !isEmpty(option);
};

const validateNetworkCIDR = (cidr) => {
  return validateCidr(cidr) && validateSpace(cidr);
};

const validateNetworkDomain = (domain) => {
  return validateURL(domain) && validateSpaces(domain) && validateLength(domain, 255) && !isEmpty(domain);
};

const validateUnrequiredInput = (input) => {
  return !(isNull(input) || isBlank(input));
};

export { validateSelect, validateNetworkCIDR, validateNetworkDomain, validateUnrequiredInput };
