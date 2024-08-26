import ipaddress
import re
from enum import Enum
from urllib.parse import urlparse


class StringType(str, Enum):
    IP4HOST = "IP4HOST"
    IP4NET = "IP4NET"
    IP4DEFAULT = "IP4DEFAULT"
    IP6HOST = "IP6HOST"
    IP6NET = "IP6NET"
    IP6DEFAULT = "IP6DEFAULT"
    IP = "IP"
    CIDR = "CIDR"
    FQDN = "FQDN"
    DOMAIN = "DOMAIN"
    URL = "URL"
    EMAIL = "EMAIL"
    HASH = "HASH"
    FILE = "FILE"
    USERAGENT = "USERAGENT"
    ASN = "ASN"
    SYSTEM = "SYSTEM"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class StringIdentifier:
    regex_map = {
        StringType.DOMAIN: r"^(((?!-))(xn--|_)?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})(?=.*[a-zA-Z])[a-z0-9]+$",
        StringType.URL: r"\bhttps?://[^\s/$.?#].[^\s]*\b",
        StringType.EMAIL: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    }
    network_map = {
        StringType.IP4HOST: StringType.CIDR,
        StringType.IP4NET: StringType.CIDR,
        StringType.IP4DEFAULT: StringType.CIDR,
        StringType.IP6HOST: StringType.CIDR,
        StringType.IP6NET: StringType.CIDR,
        StringType.IP6DEFAULT: StringType.CIDR,
        StringType.IP: StringType.CIDR,
        StringType.CIDR: StringType.CIDR,
        StringType.FQDN: StringType.DOMAIN,
        StringType.DOMAIN: StringType.DOMAIN,
        StringType.URL: StringType.UNKNOWN,
        StringType.EMAIL: StringType.UNKNOWN,
        StringType.HASH: StringType.UNKNOWN,
        StringType.FILE: StringType.UNKNOWN,
        StringType.USERAGENT: StringType.UNKNOWN,
        StringType.ASN: StringType.UNKNOWN,
        StringType.SYSTEM: StringType.UNKNOWN,
        StringType.OTHER: StringType.UNKNOWN,
        StringType.UNKNOWN: StringType.UNKNOWN,
    }
    artifact_map = {
        StringType.IP4HOST: StringType.IP,
        StringType.IP4NET: StringType.IP,
        StringType.IP4DEFAULT: StringType.IP,
        StringType.IP6HOST: StringType.IP,
        StringType.IP6NET: StringType.IP,
        StringType.IP6DEFAULT: StringType.IP,
        StringType.IP: StringType.IP,
        StringType.CIDR: StringType.IP,
        StringType.FQDN: StringType.FQDN,
        StringType.DOMAIN: StringType.DOMAIN,
        StringType.URL: StringType.URL,
        StringType.EMAIL: StringType.EMAIL,
        StringType.HASH: StringType.HASH,
        StringType.FILE: StringType.FILE,
        StringType.USERAGENT: StringType.USERAGENT,
        StringType.ASN: StringType.ASN,
        StringType.SYSTEM: StringType.SYSTEM,
        StringType.OTHER: StringType.OTHER,
        StringType.UNKNOWN: StringType.OTHER,
    }

    def __init__(self, input_string: str, **kwargs):
        self.input_string = input_string
        self.input_type = StringType.UNKNOWN
        self.parsed_string = None
        self.parsed_type = StringType.UNKNOWN
        self.network_type = StringType.UNKNOWN
        self.artifact_type = StringType.UNKNOWN
        self.parsed_obj = None
        self._identify(self.input_string)

    def _identify(self, input_string: str):
        self.input_string = input_string
        g = StringIdentifier.guess(input_string)
        self.input_type = g

        if g in StringIdentifier.get_network_address_types():
            self.parsed_string = input_string
            self.parsed_type = g
        elif g == StringType.URL:
            self.parsed_string = urlparse(input_string).hostname
            self.parsed_type = StringIdentifier.guess(self.parsed_string)
        elif g == StringType.EMAIL:
            self.parsed_string = input_string.split("@")[1]
            self.parsed_type = StringType.DOMAIN

        if (
            self.parsed_string
            and self.parsed_type in self.__class__.get_cidr_address_types()
        ):
            self.parsed_obj = ipaddress.ip_network(self.parsed_string)
            self.parsed_string = self.parsed_obj.compressed

        self.network_type = StringIdentifier.map_type_network(self.parsed_type)
        self.artifact_type = StringIdentifier.map_type_artifact(self.input_type)

    @classmethod
    def match_regex(cls, typ, input_string):
        return re.match(cls.regex_map[typ], input_string) != None

    @classmethod
    def all_network_types(cls):
        seen = set()
        return [x for x in cls.network_map.values() if not (x in seen or seen.add(x))]

    @classmethod
    def all_artifact_types(cls):
        seen = set()
        return [x for x in cls.artifact_map.values() if not (x in seen or seen.add(x))]

    @classmethod
    def get_network_address_types(cls):
        return cls.get_cidr_address_types() + cls.get_domain_address_types()

    @classmethod
    def get_cidr_address_types(cls):
        return [
            StringType.IP4HOST,
            StringType.IP4NET,
            StringType.IP4DEFAULT,
            StringType.IP6HOST,
            StringType.IP6NET,
            StringType.IP6DEFAULT,
            StringType.IP,
            StringType.CIDR,
        ]

    @classmethod
    def get_domain_address_types(cls):
        return [StringType.DOMAIN, StringType.FQDN]

    @classmethod
    def guess(cls, input_string):
        try:
            cidr = ipaddress.ip_network(input_string)
            if cidr.version == 4:
                if cidr.prefixlen == 32:
                    return StringType.IP4HOST
                elif cidr.prefixlen == 0:
                    cidr.prefixlen
                    return StringType.IP4DEFAULT
                else:
                    return StringType.IP4NET
            else:
                if cidr.prefixlen == 128:
                    return StringType.IP6HOST
                elif cidr.prefixlen == 0:
                    return StringType.IP6DEFAULT
                else:
                    return StringType.IP6NET
        except ValueError:
            for typ, pattern in cls.regex_map.items():
                if re.match(pattern, input_string):
                    return typ

        return StringType.UNKNOWN

    @classmethod
    def map_type_network(cls, string_type):
        return cls.network_map[string_type]

    @classmethod
    def map_type_artifact(cls, string_type):
        return cls.artifact_map[string_type]
