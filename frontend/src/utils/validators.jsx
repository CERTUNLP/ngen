// import IPCIDR from 'ip-cidr';
// import isCidr from 'is-cidr';
import { Address4, Address6 } from "ip-address";

const validateEmail = (email) => {
  return /^(([^<>()\]\\.,;:\s@"]+(\.[^<>()\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
    email
  );
};

const validateFieldText = (text) => {
  if (text === "") {
    return true;
  }
  return /^[A-Za-zÁÉÍÓÚáéíóúñÑ' ]+$/g.test(text);
};

const validateUsername = (text) => {
  if (text === "") {
    return true;
  }
  return /^[a-zA-Z0-9@.+_-]+$/.test(text);
};

const validateSpaces = (text) => {
  return !/ /.test(text);
};
const validateSpace = (text) => {
  if (text === undefined) {
    return true;
  }
  return text.trim() !== "";
};

const validateLength = (text, maxLength) => {
  return !!text && text.length <= maxLength;
};

const isEmpty = (text) => {
  return text?.trim().length === 0;
};

const isBlank = (text) => {
  return text === "";
};

const isNull = (text) => {
  return text === undefined;
};

const validateAlphanumeric = (text) => {
  if (text === "") {
    return true;
  }
  return /^[A-Za-zÁÉÍÓÚáéíóúñÑ'0-9 ]+$/g.test(text);
};

const validateNumbers = (text) => {
  if (text === "") {
    return true;
  }
  return /^[0-9]+$/g.test(text);
};

const validateURL = (str) => {
  var pattern = /\bhttps?:\/\/[^\s/$.?#].[^\s]*\b/i;
  return str === "*" || !!pattern.test(str);
};
const validateHours = (hours) => {
  return /^(0?[0-9]|1[0-9]|2[0-3])$/.test(hours);
};
const validateMinutes = (minutes) => {
  return /^(0?[0-9]|[1-5][0-9])$/.test(minutes);
};

const validateNumber = (number) => {
  if (number === "") {
    return true;
  }
  return /^[0-9]+$/g.test(number);
};

const validateCidr = (address) => {
  let addr;

  try {
    addr = new Address4(address);
  } catch {}
  try {
    addr = new Address6(address);
  } catch {}

  try {
    if (!addr) {
      return false;
    }
    // Obtener la dirección de red (primer dirección del rango CIDR)
    const startAddress = addr.startAddress().correctForm();

    return addr.addressMinusSuffix === startAddress;
  } catch {
    return false;
  }
};

const validateIP = (ip) => {
  const patronIP = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
  if (!patronIP.test(ip)) {
    return false; // No coincide con el formato xxx.xxx.xxx.xxx
  }

  const octets = ip.split(".");
  for (let i = 0; i < octets.length; i++) {
    const octet = parseInt(octets[i], 10);
    if (octet < 0 || octet > 255) {
      return false; // Cada octet debe estar entre 0 y 255
    }
  }

  return true; // La IP es válida
};

const validateAutonomousSystem = (autonomousSystem) => {
  var min = 0;
  var max = 4294967295;

  return autonomousSystem > min && autonomousSystem <= max;
};

const validateUserAgent = (userAgent) => {
  return /^[a-zA-Z0-9\s.,/#!$%^&*;:{}=\-_`~()@+?><[\]+]*$/.test(userAgent);
};

const validateSubdomain = (dominio) => {
  // Expresión regular para verificar la sintaxis del dominio
  var patron = /^[a-zA-Z0-9]+([-.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$/;
  // Verificar si el dominio coincide con el patrón
  return patron.test(dominio);
};

const validateDomain = (dominio) => {
  // Expresión regular para verificar la sintaxis del dominio
  // igual a validateSubdomain pero con posibilidad de solo tld
  var patron = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$|^[a-zA-Z]{2,}$/;
  // Verificar si el dominio coincide con el patrón
  return patron.test(dominio);
}

const validateFile = (file) => {
  return file !== null;
};

const validateHexadecimal32 = (valueHexadecimal) => {
  // Verificar la longitud de la cadena
  if (valueHexadecimal.length !== 32) {
    return false;
  }
  // Verificar si la cadena es hexadecimal
  return /^[0-9a-fA-F]+$/.test(valueHexadecimal);
};

const validateHexadecimal40 = (valueHexadecimal) => {
  // Verificar la longitud de la cadena
  if (valueHexadecimal.length !== 40) {
    return false;
  }
  // Verificar si la cadena es hexadecimal
  return /^[0-9a-fA-F]+$/.test(valueHexadecimal);
};

const validateHexadecimal64 = (valueHexadecimal) => {
  // Verificar la longitud de la cadena
  if (valueHexadecimal.length !== 64) {
    return false;
  }
  // Verificar si la cadena es hexadecimal
  return /^[0-9a-fA-F]+$/.test(valueHexadecimal);
};

const validateHexadecimal128 = (valueHexadecimal) => {
  // Verificar la longitud de la cadena
  if (valueHexadecimal.length !== 128) {
    return false;
  }
  // Verificar si la cadena es hexadecimal
  return /^[0-9a-fA-F]+$/.test(valueHexadecimal);
};

export {
  validateHours,
  validateMinutes,
  validateEmail,
  validateFieldText,
  validateUsername,
  validateSpaces,
  validateNumber,
  validateAlphanumeric,
  validateNumbers,
  validateSpace,
  validateURL,
  validateFile,
  validateCidr,
  validateLength,
  isEmpty,
  isBlank,
  isNull,
  validateIP,
  validateAutonomousSystem,
  validateUserAgent,
  validateSubdomain,
  validateDomain,
  validateHexadecimal32,
  validateHexadecimal40,
  validateHexadecimal64,
  validateHexadecimal128
};
