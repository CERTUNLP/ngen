import { isBlank, isEmpty, isNull, validateCidr, validateLength, validateSpace, validateSpaces, validateURL } from "../validators";

const validateSelect = (option) => {
  return !isEmpty(option);
};

const validateNetworkCIDR = (cidr) => {
  console.log(cidr, validateCidr(cidr), validateSpace(cidr));
  return validateCidr(cidr) && validateSpace(cidr);
};

const validateNetworkDomain = (domain) => {
  return validateURL(domain) && validateSpaces(domain) && validateLength(domain, 255) && !isEmpty(domain);
};

const validateUnrequiredInput = (input) => {
  return !(isNull(input) || isBlank(input));
};

const validateAddressValue = (addressValue) => {
  return validateNetworkCIDR(addressValue) || validateNetworkDomain(addressValue);
};

const validateAddressValueOrNetworkOrDomain = (obj) => {
  return validateAddressValue(obj.address_value) || validateNetworkCIDR(obj.cidr) || validateNetworkDomain(obj.domain);
}

export { validateSelect, validateNetworkCIDR, validateNetworkDomain, validateUnrequiredInput, validateAddressValue, validateAddressValueOrNetworkOrDomain };
