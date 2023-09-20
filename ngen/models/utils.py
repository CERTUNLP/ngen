import ipaddress
import re

from auditlog.models import AuditlogHistoryField
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from django.utils.translation import gettext
from django_lifecycle import hook, BEFORE_DELETE, BEFORE_UPDATE, LifecycleModelMixin, BEFORE_CREATE
from model_utils.models import TimeStampedModel
from netfields import CidrAddressField, NetManager
from django.core.exceptions import ValidationError
from treebeard.al_tree import AL_Node
from constance import config
from enum import Enum
from urllib.parse import urlparse

import ngen


class StringType(str, Enum):
    IP4HOST = 'IP4HOST'
    IP4NET = 'IP4NET'
    IP4DEFAULT = 'IP4DEFAULT'
    IP6HOST = 'IP6HOST'
    IP6NET = 'IP6NET'
    IP6DEFAULT = 'IP6DEFAULT'
    IP = 'IP'
    CIDR = 'CIDR'
    FQDN = 'FQDN'
    DOMAIN = 'DOMAIN'
    URL = 'URL'
    EMAIL = 'EMAIL'
    HASH = 'HASH'
    FILE = 'FILE'
    USERAGENT = 'USERAGENT'
    ASN = 'ASN'
    SYSTEM = 'SYSTEM'
    OTHER = 'OTHER'
    UNKNOWN = 'UNKNOWN'


class StringIdentifier():
    regex_map = {
        StringType.DOMAIN: r'^(((?!-))(xn--|_)?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$',
        StringType.URL: r'\bhttps?://[^\s/$.?#].[^\s]*\b',
        StringType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
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
            self.parsed_string = input_string.split('@')[1]
            self.parsed_type = StringType.DOMAIN

        if self.parsed_string and self.parsed_type in self.__class__.get_cidr_address_types():
            self.parsed_obj = ipaddress.ip_network(self.parsed_string)
            self.parsed_string = self.parsed_obj.compressed

        self.network_type = StringIdentifier.map_type_network(
            self.parsed_type)
        self.artifact_type = StringIdentifier.map_type_artifact(
            self.input_type)

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
        return [StringType.IP4HOST, StringType.IP4NET, StringType.IP4DEFAULT,
                StringType.IP6HOST, StringType.IP6NET, StringType.IP6DEFAULT,
                StringType.IP, StringType.CIDR]

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


class NgenModel(TimeStampedModel):
    history = AuditlogHistoryField()

    class Meta:
        abstract = True


class NgenTreeModel(AL_Node):
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True,
                               blank=True, db_index=True, related_name='children')

    class Meta:
        abstract = True

    def get_ancestors_related(self, callback, flat=False):
        return self.get_related(self.get_ancestors, callback, flat)

    def get_descendants_related(self, callback, flat=False):
        return self.get_related(self.get_descendants, callback, flat)

    @staticmethod
    def get_related(related_callback, callback, flat=False):
        related = []
        for ancestor in related_callback():
            results = callback(ancestor)
            if results:
                if flat:
                    for result in results:
                        related.insert(0, result)
                else:
                    related.insert(0, results)
        return related

    @classmethod
    def get_parents(cls):
        return cls.objects.filter(parent__isnull=True)

    def is_child(self):
        return self.parent is not None

    def is_parent(self):
        return self.children.exists()

    @classmethod
    def find_problems(cls):
        pass

    @classmethod
    def fix_tree(cls):
        pass


class NgenMergeableModel(LifecycleModelMixin, NgenTreeModel):
    class Meta:
        abstract = True

    @property
    def blocked(self) -> bool:
        raise NotImplementedError

    @property
    def mergeable(self) -> bool:
        return not self.merged and not self.blocked

    @property
    def merged(self) -> bool:
        return self.is_child()

    def mergeable_with(self, child: 'NgenMergeableModel') -> bool:
        if self.uuid == child.uuid:
            raise ValidationError(
                {'parent': gettext('The parent must not be the same instance.')})
        if not self.mergeable:
            raise ValidationError(
                {'parent': gettext('The parent is not mergeable or is blocked.')})
        if child.blocked:
            raise ValidationError(
                gettext('The child is not mergeable or is blocked.'))
        return True

    def merge(self, child: 'NgenMergeableModel'):
        for child in child.children.all():
            self.children.add(child)

    @hook(BEFORE_UPDATE, when="parent", has_changed=True)
    @hook(BEFORE_CREATE, when="parent", was=None)
    def parent_changed(self):
        if self.initial_value('parent') is None:
            if self.parent and self.parent.mergeable_with(self) and not self._state.adding:
                self.parent.merge(self)
        else:
            raise ValidationError(
                gettext('Parent of merged instances can\'t be modified'))

    @hook(BEFORE_DELETE)
    def delete_children(self):
        for child in self.get_descendants():
            child.delete()


class NgenEvidenceMixin(models.Model):
    evidence = GenericRelation('ngen.Evidence')
    _files = []

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        for evidence in self.evidence.all():
            evidence.delete()
        super(NgenEvidenceMixin, self).delete()

    def save(self, **kwargs):
        super(NgenEvidenceMixin, self).save()
        for file in self.files:
            self.add_evidence(file)

    def evidence_path(self):
        return 'evidence/%s/%s' % (self.__class__.__name__, self.id)

    def add_evidence(self, file):
        self.evidence.get_or_create(file=file)

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, files):
        self._files = files


class NgenPriorityMixin(models.Model):
    priority = models.ForeignKey('Priority', models.PROTECT)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.priority_id:
            self.priority = ngen.models.Priority.default_priority()
        super().save(*args, **kwargs)


class AddressManager(NetManager):
    def cidr_parents_of(self, cidr: str):
        return self.filter(cidr__net_contains_or_equals=cidr).order_by('-cidr')

    def domain_parents_of(self, domain: str):
        query = Q(domain='*') | Q(domain=domain)
        partition = domain.partition('.')[-1]
        while partition:
            query |= Q(domain=partition)
            partition = partition.partition('.')[-1]
        return self.filter(query).order_by(Length('domain').desc())

    def parents_of(self, address: 'NgenAddressModel'):
        if address.cidr:
            return self.cidr_parents_of(str(address.address))
        elif address.domain:
            return self.domain_parents_of(str(address.address))
        return self.none()

    def parent_of(self, address: 'NgenAddressModel'):
        return self.parents_of(address)

    def defaults(self):
        return self.filter(Q(cidr__prefixlen=0) | Q(domain='*'))

    def defaults_ipv4(self):
        return self.filter(cidr__prefixlen=0, cidr__family=4)

    def defaults_ipv6(self):
        return self.filter(cidr__prefixlen=0, cidr__family=6)

    def defaults_domain(self):
        return self.filter(domain='*')


class NgenAddressModel(models.Model):
    cidr = CidrAddressField(null=True, default=None, blank=True)
    domain = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    address_value = models.CharField(
        max_length=255, null=False, default='', blank=True)
    objects = AddressManager()
    address = None
    sid = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assign_address()

    def assign_address(self):
        if self.address_value:
            self.sid = StringIdentifier(self.address_value)
            if self.sid.network_type == StringType.CIDR:
                self.cidr = self.sid.parsed_string
            elif self.sid.network_type == StringType.DOMAIN:
                self.domain = self.sid.parsed_string

        if self.cidr:
            try:
                self.address = self.AddressIpv4(self.cidr)
            except ValueError:
                self.address = self.AddressIpv6(self.cidr)
            self.cidr = self.address.sanitized()
            return self.address
        elif self.domain != None:
            self.address = self.AddressDomain(self.domain)
            self.domain = self.address.sanitized()
            return self.address
        return None

    def validate_addresses(self):
        if not self.address_value and not self.cidr and self.domain == None:
            msg = 'At least cidr or domain must be setted'
            raise ValidationError({'cidr': [msg], 'domain': [msg]})
        elif self.cidr and self.domain != None:
            msg = 'cidr and domain are mutually exclusive'
            raise ValidationError(
                {'address_value': [msg], 'cidr': [msg], 'domain': [msg]})

        if self.address_value:
            self.sid = StringIdentifier(self.address_value)
            if self.cidr:
                if ipaddress.ip_network(self.cidr) != self.sid.parsed_obj:
                    msg = 'cidr is not in address_value'
                    raise ValidationError(
                        {'cidr': [msg], 'address_value': [msg]})
            elif self.domain:
                if not self.domain == self.sid.parsed_string:
                    msg = 'domain is not in address_value'
                    raise ValidationError(
                        {'domain': [msg], 'address_value': [msg]})

    def clean(self):
        # Should be called by subclasses if they override clean()
        self.validate_addresses()

        if not self.assign_address():
            raise ValidationError(
                gettext('Address must be either a cidr or a domain.'))

        if not self.address.is_valid():
            raise ValidationError(
                {self.field_name(): [f'Must be a valid {self.field_name()}']})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __eq__(self, other: 'NgenAddressModel'):
        if isinstance(other, NgenAddressModel):
            return self.address == other.address

    def __str__(self):
        return self.address.network_string()

    def __contains__(self, other: 'NgenAddressModel'):
        # b.address._address.subnet_of(a.address._address)
        if isinstance(other, NgenAddressModel):
            return other.address in self.address

    def __hash__(self) -> int:
        return super().__hash__()

    def is_default(self):
        return self.address.is_default()

    def field_name(self):
        return self.address.field_name()

    def default(self):
        return self.address.default()

    def network_address(self):
        return self.address.network_address

    class Address:
        _address = None

        def __init__(self, address: str):
            self.address = address

        @property
        def address(self):
            return self._address

        @address.setter
        def address(self, value):
            self._address = self.create_address_object(value)

        def __eq__(self, other):
            return self.address == other.address

        def __contains__(self, other):
            return self.in_range(other)

        def __str__(self):
            return self.address

        def is_default(self):
            return self.address_mask() == 0

    class AddressIp(Address):

        def address_mask(self):
            return self._address.prefixlen

        def in_range(self, other):
            return other._address > self._address

        def __str__(self):
            return self.address.compressed

        def field_name(self):
            return 'cidr'

        def sanitized(self):
            return self.address.compressed

        def network_string(self):
            return self.address.compressed

        def is_valid(self):
            return self.address != None

        def network_address(self):
            return self.address.network_address

    class AddressIpv4(AddressIp):

        def create_address_object(self, address: str):
            return ipaddress.IPv4Network(address)

        def is_ipv4(self):
            return True

        def is_ipv6(self):
            return False

        def default(self):
            return '0.0.0.0/0'

    class AddressIpv6(AddressIp):

        def create_address_object(self, address: str):
            return ipaddress.IPv6Network(address)

        def is_ipv4(self):
            return False

        def is_ipv6(self):
            return True

        def default(self):
            return '::/0'

    class AddressDomain(Address):

        def address_mask(self):
            if self.address in ['*', '']:
                return 0
            return len(self.address.split('.'))

        def create_address_object(self, address):
            # return address.replace('*','').strip().lower().split('/')[0]
            a = address.replace(
                '*', '').strip().strip('.').lower().split('/')[0]
            if a == '':
                return '*'
            return a

        def in_range(self, other):
            address_set = set(self.address.split('.'))
            address_set_other = set(other.address.split('.'))

            if address_set == address_set_other:
                return True

            if address_set_other > address_set:
                return address_set & address_set_other == address_set

            return False

        def default(self):
            return '*'

        def field_name(self):
            return 'domain'

        def sanitized(self):
            return self.create_address_object(self.address)

        def network_string(self):
            if self.is_default():
                return '*'
            return f'*.{self.address}'

        def network_with_mask(self):
            return f'{self.address}/{self.address_mask()}'

        def is_valid(self):
            return self.address == '*' or StringIdentifier.match_regex(StringType.DOMAIN, self.address)

        def network_address(self):
            return self.address

        # def __str__(self):
            # if self.is_default():
            #     return '*/0'
            # return f'{self.address}/{self.address_mask()}'
