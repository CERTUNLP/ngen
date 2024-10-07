import whois
import whoisit
import requests
from ngen.models.common.parsing import StringIdentifier, StringType
import socket


class ContactLookupService:

    @staticmethod
    def whois_lookup(domain, str_type=None):
        """
        Realiza la búsqueda de WHOIS para un dominio.
        """
        try:
            whois_data = whois.whois(domain)
            return {"raw": whois_data, "abuse_contact": whois_data.get("abuse_contact")}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def rdap_lookup(ip_or_domain, str_type=None):
        """
        Realiza la búsqueda de RDAP (Resource Data Access Protocol) para una IP o dominio.
        """
        try:
            whoisit.bootstrap()
            if str_type == StringType.ASN:
                rdap_data = whoisit.asn(ip_or_domain)
            elif StringIdentifier.network_map[str_type] == StringType.IP:
                rdap_data = whoisit.ip(ip_or_domain)
            elif StringIdentifier.network_map[str_type] == StringType.DOMAIN:
                rdap_data = whoisit.domain(ip_or_domain)
            else:
                rdap_data = whoisit.entity(ip_or_domain)
            return {
                "raw": rdap_data,
                "abuse_contact": rdap_data.get("entities")[0].get("email"),
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def security_txt_lookup(domain, str_type=None):
        """
        Intenta obtener el archivo security.txt del dominio.
        """
        try:
            url = f"https://{domain}/.well-known/security.txt"
            response = requests.get(url)
            if response.status_code == 200:
                return {
                    "url": url,
                    "raw": response.text,
                    "abuse_contact": response.text.split("\n")[1].split(":")[1].strip(),
                }
            else:
                return {"error": "No security.txt found."}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def resolve_ip(domain):
        """
        Resuelve la dirección IP de un dominio.
        """
        try:
            return socket.gethostbyname(domain)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_contact_info_for_type(domain_or_ip, str_type):
        """
        Realiza la búsqueda de información de contacto combinada de WHOIS, RDAP y security.txt.
        """
        contact_info = {
            "whois": ContactLookupService.whois_lookup(domain_or_ip, str_type),
            "rdap": ContactLookupService.rdap_lookup(domain_or_ip, str_type),
            "security_txt": ContactLookupService.security_txt_lookup(
                domain_or_ip, str_type
            ),
        }
        return contact_info

    @staticmethod
    def get_contact_info(domain_or_ip):
        """
        Realiza la búsqueda de información de contacto combinada de WHOIS, RDAP y security.txt.
        """
        str_type = StringIdentifier.guess(domain_or_ip)
        res1 = ContactLookupService.get_contact_info_for_type(domain_or_ip, str_type)
        result = {
            "query": domain_or_ip,
            "type": StringIdentifier.guess(domain_or_ip),
            "result": res1,
        }

        if StringIdentifier.network_map[str_type] == StringType.DOMAIN:
            ip = ContactLookupService.resolve_ip(domain_or_ip)
            str_type2 = StringIdentifier.guess(ip)
            res2 = ContactLookupService.get_contact_info_for_type(ip, str_type2)
            result["secondary_query"] = {
                "query": ip,
                "type": StringIdentifier.guess(ip),
                "result": res2,
            }

        return result
