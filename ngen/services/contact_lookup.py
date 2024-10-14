import whois
import whoisit
import socket
import requests
import logging

from urllib.parse import urlparse
from publicsuffix2 import get_sld

from ngen.models.common.parsing import StringIdentifier, StringType


logger = logging.getLogger(__name__)


class ContactLookupService:

    @staticmethod
    def whois_lookup(domain, str_type=None):
        """
        Perform WHOIS lookup for a domain.

        https://www.rfc-editor.org/rfc/rfc2142#section-4
        """
        try:
            if not StringIdentifier.network_map[str_type] in [
                StringType.DOMAIN,
                StringType.CIDR,
            ]:
                return {"error": "Invalid domain or IP."}

            whois_data = whois.whois(domain)
            emails = whois_data.get("emails", [])
            return {
                "raw": whois_data,
                "abuse_emails": emails if type(emails) == list else [emails],
            }

        except Exception as e:
            logger.error(f"Error in WHOIS lookup: {e}")
            return {"error": str(e)}

    @staticmethod
    def rdap_lookup(ip_or_domain, str_type=None, url=None):
        """
        Perform RDAP lookup for a domain or IP.

        https://www.rfc-editor.org/rfc/rfc2142#section-4
        """
        try:
            if str_type == None:
                return {"error": "Invalid domaian, IP or ASN value."}

            res = {}
            whoisit.bootstrap()
            if str_type == StringType.ASN:
                res = whoisit.asn(ip_or_domain)
            elif StringIdentifier.network_map[str_type] == StringType.CIDR:
                res = whoisit.ip(ip_or_domain)
            elif StringIdentifier.network_map[str_type] == StringType.DOMAIN:
                res = whoisit.domain(ip_or_domain)
            else:
                return {"error": "Invalid domain, IP or ASN."}

            res.pop("network", None)

            logger.debug(f"RDAP lookup result: {res}")
            # Using else with this could be dangerous. I don't know what
            # this library does with the string and maybe we should check
            # it for every lookup
            #     res = whoisit.entity(ip_or_domain)
            emails = []
            try:
                e = res.get("entities", {})
                for typ in ["abuse", "technical", "administrative", "registrant"]:
                    if typ in e:
                        for card in e[typ]:
                            if "email" in card:
                                emails.append(card["email"])
                        if len(emails) > 0:
                            break
            except Exception as e:
                logger.error(f"Error in RDAP lookup: {e}")

            return {"raw": res, "abuse_emails": emails}

        except Exception as e:
            logger.error(f"Error in RDAP lookup: {e}")
            return {"error": str(e)}

    @staticmethod
    def securitytxt_lookup(domain, str_type=None, url=None):
        """
        Perform security.txt lookup for a domain.

        https://datatracker.ietf.org/doc/html/rfc9116#section-2.5.3
        """
        try:
            if (
                not StringIdentifier.network_map[str_type]
                in [StringType.DOMAIN, StringType.CIDR]
                and not str_type == StringType.URL
            ):
                return {"error": "Invalid domain or URL."}

            if url and str_type == StringType.URL:
                server = "/".join(url.split("/")[:3])
                parsed_url = f"{server}/.well-known/security.txt"
            else:
                parsed_url = f"https://{domain}/.well-known/security.txt"

            response = requests.get(parsed_url)

            if response.status_code == 200:
                abuse_emails = [
                    l.split(":")[-1].strip()
                    for l in response.text.lower().split("\n")
                    if l.startswith("contact: mailto:")
                ]
                return {
                    "url": parsed_url,
                    "raw": response.text,
                    "abuse_emails": abuse_emails,
                }

            else:
                return {"error": "No security.txt found."}

        except Exception as e:
            logger.error(f"Error in security txt lookup: {e}")
            return {"error": str(e)}

    @staticmethod
    def resolve_ip(domain):
        """
        Resuelve la dirección IP de un dominio.
        """
        try:
            return socket.gethostbyname(domain)

        except Exception as e:
            logger.error(f"Error in resolving domain: {e}")
            raise e

    @staticmethod
    def get_contact_info_for_type(domain_or_ip, str_type4, url=None):
        """
        Realiza la búsqueda de información de contacto basica de WHOIS, RDAP y security.txt.
        """
        contact_info = {
            "whois": ContactLookupService.whois_lookup(domain_or_ip, str_type4),
            "rdap": ContactLookupService.rdap_lookup(domain_or_ip, str_type4),
            "securitytxt": ContactLookupService.securitytxt_lookup(
                domain_or_ip, str_type4, url=url
            ),
        }

        return {
            "query": domain_or_ip,
            "type": str_type4,
            "data": contact_info,
            "abuse_emails": list(
                set(
                    contact_info["whois"].get("abuse_emails", [])
                    + contact_info["rdap"].get("abuse_emails", [])
                    + contact_info["securitytxt"].get("abuse_emails", [])
                )
            ),
        }

    @staticmethod
    def get_contact_info_of_type(domain_or_ip, str_type, url=None):
        """
        Realiza la búsqueda de información de contacto combinada de WHOIS, RDAP y security.txt.
        """
        return ContactLookupService.get_contact_info_for_type(
            domain_or_ip, str_type, url=url
        )

    @staticmethod
    def get_contact_info(url_ip_domain):
        """
        Perform combined WHOIS, RDAP and security.txt lookup for a domain, IP or URL.

        Returns a dictionary with the results of the lookups with the following
        keys:
        - original: Lookup results for the original input.
        - hostname: Lookup results for the hostname extracted from the URL. If the
            input is a domain, this will be the same as the original lookup. If the original
            input is an IP, this will be None.
        - solved_domain: Lookup results for the IP of the domain. If the original input
            is a IP, this will be None. If the original input is a domain, this will be the
            lookup results for the IP of the domain. If the original input is a URL, this will
            be the lookup results for the IP of the hostname.
        - sld: Lookup results for the second level domain of the hostname. If the original
            input is an IP, this will be None. If the original input is a domain, this will be
            the lookup results for the second level domain of the domain. If the original input
            is a URL, this will be the lookup results for the second level domain of the hostname
            if the hostname is a domain. If the original input is a SLD this will be the same as
            the hostname lookup and the original lookup.
        - abuse_emails: List of unique abuse emails found in all the lookups.
        """
        result = {}

        # Guess the type of the query input
        original_type = StringIdentifier.guess(url_ip_domain)
        # Get the lookup for the original query input
        result["original"] = ContactLookupService.get_contact_info_of_type(
            url_ip_domain, original_type
        )

        hostname_query = None
        hostname_type = None
        solved_domain_query = None
        url = None

        try:
            if original_type == StringType.URL:
                # Extract the hostname from the URL
                url = url_ip_domain
                hostname_query = urlparse(url_ip_domain).hostname
                hostname_type = StringIdentifier.guess(hostname_query)
            elif original_type == StringType.DOMAIN:
                # Use the domain as the hostname
                hostname_query = url_ip_domain
                hostname_type = StringType.DOMAIN
        except Exception as e:
            logger.error(f"Error in extracting hostname <{url_ip_domain}>: {e}")

        if hostname_query:
            # Get the lookup for the hostname
            result["hostname"] = ContactLookupService.get_contact_info_of_type(
                hostname_query, hostname_type, url=url
            )

            if hostname_type == StringType.DOMAIN:
                # If original input is a domain or an url with a domain
                # Ex: example.com or http://sub.example.com/path

                try:
                    # Get the IP of domain
                    solved_domain_query = ContactLookupService.resolve_ip(
                        hostname_query
                    )
                    solved_domain_type = StringIdentifier.guess(solved_domain_query)
                    result["solved_domain"] = (
                        ContactLookupService.get_contact_info_of_type(
                            solved_domain_query, solved_domain_type, url=url
                        )
                    )
                except Exception as e:
                    logger.error(
                        f"Error in resolving domain <{hostname_query}> from <{url_ip_domain}>: {e}"
                    )

                try:
                    # Get the second level domain
                    sld = get_sld(hostname_query)

                    if sld == hostname_query:
                        result["sld_hostname"] = result["hostname"]
                    elif sld == solved_domain_query:
                        result["sld_solved_domain"] = result["solved_domain"]
                    else:
                        result["sld"] = ContactLookupService.get_contact_info_of_type(
                            sld, StringType.DOMAIN, url=url
                        )
                except Exception as e:
                    logger.error(
                        f"Error in getting SLD <{hostname_query}> from <{url_ip_domain}>: {e}"
                    )

        result["abuse_emails"] = list(
            set(
                result.get("original", {}).get("abuse_emails", [])
                + result.get("hostname", {}).get("abuse_emails", [])
                + result.get("solved_domain", {}).get("abuse_emails", [])
                + result.get("sld", {}).get("abuse_emails", [])
            )
        )

        return result
