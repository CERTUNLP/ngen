import { isBlank, isEmpty, isNull, validateCidr, validateDomain, validateLength, validateSpace, validateSpaces, validateURL } from "../validators";

const validateSelect = (option) => {
  return !isEmpty(option);
};

const validateNetworkCIDR = (cidr) => {
  return validateCidr(cidr) && validateSpace(cidr);
};

const validateNetworkDomain = (domain) => {
  return validateDomain(domain) && validateSpaces(domain) && validateLength(domain, 255) && !isEmpty(domain);
};

const validateUnrequiredInput = (input) => {
  return !(isNull(input) || isBlank(input));
};

const validateAddressValue = (addressValue) => {
  return validateNetworkCIDR(addressValue) || validateNetworkDomain(addressValue);
};

const validateAddressValueOrNetworkOrDomainInObj = (obj) => {
  return validateAddressValue(obj.address_value) || validateNetworkCIDR(obj.cidr) || validateNetworkDomain(obj.domain);
}

const validateAddressValueOrNetworkOrDomain = (input) => {
  return validateAddressValue(input) || validateNetworkCIDR(input) || validateNetworkDomain(input);
}

export { validateSelect, validateNetworkCIDR, validateNetworkDomain, validateUnrequiredInput, validateAddressValue, validateAddressValueOrNetworkOrDomainInObj, validateAddressValueOrNetworkOrDomain };
