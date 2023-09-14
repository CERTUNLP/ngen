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


class StringType(Enum):
    IP4HOST = (1, None)
    IP4NET = (2, None)
    IP4DEFAULT = (3, None)
    IP6HOST = (4, None)
    IP6NET = (5, None)
    IP6DEFAULT = (6, None)
    DOMAIN = (
        7, r'^(((?!-))(xn--|_)?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$')
    URL = (8, r'\bhttps?://[^\s/$.?#].[^\s]*\b')
    EMAIL = (9, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
    HASH = (6, None)
    FILE = (9, None)
    USERAGENT = (10, None)
    ASN = (11, None)
    SYSTEM = (12, None)
    OTHER = (13, None)
    UNKNOWN = (14, None)

    def get_regex_pattern(self):
        return self.value[1]

    @classmethod
    def get_cidr_types(cls):
        return [StringType.IP4HOST, StringType.IP4NET, StringType.IP4DEFAULT,
                StringType.IP6HOST, StringType.IP6NET, StringType.IP6DEFAULT]

    @classmethod
    def identify(cls, string_value):
        g = StringType.guess(string_value)
        id = {
            'original_string': string_value,
            'original_type': g,
            'address_string': None,
            'adddess_type': cls.UNKNOWN,
            'is_cidr': False,
            'is_domain': False,
        }

        if g in cls.get_cidr_types() + [StringType.DOMAIN]:
            id['address_string'] = string_value
            id['adddess_type'] = g
        elif g == StringType.URL:
            id['address_string'] = urlparse(string_value).hostname
            id['adddess_type'] = StringType.guess(id['address_string'])
        elif g == StringType.EMAIL:
            id['address_string'] = string_value.split('@')[1]
            id['adddess_type'] = StringType.DOMAIN

        if id['adddess_type'] in cls.get_cidr_types():
            id['is_cidr'] = True
        elif id['adddess_type'] == StringType.DOMAIN:
            id['is_domain'] = True

        return id

    @classmethod
    def match_regex(cls, typ, input_string):
        regex = typ.get_regex_pattern()
        if not regex:
            return None
        return re.match(regex, input_string) != None

    @classmethod
    def guess(cls, input_string):
        try:
            cidr = ipaddress.ip_network(input_string)
            if cidr.version == 4:
                if cidr.prefixlen == 32:
                    return cls.IP4HOST
                elif cidr.prefixlen == 0:
                    cidr.prefixlen
                    return cls.IP4DEFAULT
                else:
                    return cls.IP4NET
            else:
                if cidr.prefixlen == 128:
                    return cls.IP6HOST
                elif cidr.prefixlen == 0:
                    return cls.IP6DEFAULT
                else:
                    return cls.IP6NET
        except ValueError:
            for address_type in cls:
                pattern = address_type.get_regex_pattern()
                if pattern:
                    if re.match(pattern, input_string):
                        return address_type

        return cls.UNKNOWN


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

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assign_address()

    def assign_address(self):
        if self.address_value:
            id_dict = StringType.identify(self.address_value)
            if id_dict['is_cidr']:
                self.cidr = id_dict['address_string']
            elif id_dict['is_domain']:
                self.domain = id_dict['address_string']

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
            msg = 'cidr or domain must be setted'
            raise ValidationError({'cidr': [msg], 'domain': [msg]})
        elif self.cidr and self.domain != None:
            msg = 'cidr and domain are mutually exclusive'
            raise ValidationError(
                {'address_value': [msg], 'cidr': [msg], 'domain': [msg]})

        if self.address_value:
            if self.cidr:
                if not str(self.cidr) in self.address_value:
                    msg = 'cidr is not in address_value'
                    raise ValidationError(
                        {'cidr': [msg], 'address_value': [msg]})
            if self.domain:
                if not self.domain in self.address_value:
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
            return self.address == '*' or StringType.match_regex(StringType.DOMAIN, self.address)

        def network_address(self):
            return self.address

        # def __str__(self):
            # if self.is_default():
            #     return '*/0'
            # return f'{self.address}/{self.address_mask()}'
