import ipaddress

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
import re

import ngen


class NgenModel(TimeStampedModel):
    history = AuditlogHistoryField()

    class Meta:
        abstract = True


class NgenTreeModel(AL_Node):
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, blank=True, db_index=True, related_name='children')

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
            raise ValidationError({'parent': gettext('The parent must not be the same instance.')})
        if not self.mergeable:
            raise ValidationError({'parent': gettext('The parent is not mergeable or is blocked.')})
        if child.blocked:
            raise ValidationError(gettext('The child is not mergeable or is blocked.'))
        return True

    def merge(self, child: 'NgenMergeableModel'):
        for child in child.children.all():
            self.children.add(child)

    @hook(BEFORE_UPDATE, when="parent", has_changed=True)
    @hook(BEFORE_CREATE, when="parent", was=None)
    def parent_changed(self):
        if self.initial_value('parent') is None:
            if self.parent and self.parent.mergeable_with(self):
                self.parent.merge(self)
        else:
            raise ValidationError(gettext('Parent of merged instances can\'t be modified'))

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
    priority = models.ForeignKey('Priority', models.DO_NOTHING)

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
    domain = models.CharField(max_length=255, null=True, default=None, blank=True)
    address = None
    objects = AddressManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assign_address()

    def assign_address(self):
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

    def clean(self):
        # Should be called by subclasses if they override clean()
        if not self.cidr and self.domain == None:
            raise ValidationError({'cidr': ['CIDR or Domain must be setted'], 'domain': ['CIDR or Domain must be setted']})
        elif self.cidr and self.domain != None:
            raise ValidationError({'cidr': ['CIDR and Domain are mutually exclusive'], 'domain': ['CIDR and Domain are mutually exclusive']})

        if not self.assign_address():
            raise ValidationError(gettext('Address must be either a CIDR or a domain.'))

        if not self.address.is_valid():
            raise ValidationError({self.field_name(): [f'Must be a valid {self.field_name()}']})

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
            a = address.replace('*','').strip().strip('.').lower().split('/')[0]
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
            domain_regex = r'^(((?!-))(xn--|_)?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$'
            return self.address == '*' or re.match(domain_regex, self.address) != None

        def network_address(self):
            return self.address

        # def __str__(self):
            # if self.is_default():
            #     return '*/0'
            # return f'{self.address}/{self.address_mask()}'
