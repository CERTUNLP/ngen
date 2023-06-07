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
from rest_framework.exceptions import ValidationError
from treebeard.al_tree import AL_Node

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
        if self is child:
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
        return self.filter(cidr__net_contains=cidr).order_by('-cidr')

    def domain_parents_of(self, domain: str):
        query = Q(domain='') | Q(domain=domain)
        partition = domain.partition('.')[-1]
        while partition:
            query |= Q(domain=partition)
            partition = partition.partition('.')[-1]
        return self.filter(query).order_by(Length('domain').desc())

    def parents_of(self, address: 'NgenAddressModel'):
        if address.cidr:
            return self.cidr_parents_of(str(address.cidr))
        elif address.domain:
            return self.domain_parents_of(address.domain)

    def parent_of(self, address: 'NgenAddressModel'):
        return self.parents_of(address).first()


class NgenAddressModel(models.Model):
    cidr = CidrAddressField(null=True, default=None, blank=True)
    domain = models.CharField(max_length=255, null=True, default=None, blank=True)
    address = None
    objects = AddressManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.cidr:
            self.address = self.AddressIp(self.cidr)
        elif self.domain:
            self.address = self.AddressDomain(self.domain)

    def __eq__(self, other: 'NgenAddressModel'):
        if isinstance(other, NgenAddressModel):
            return self.address == other.address

    def __str__(self):
        return self.address.__str__()

    def __contains__(self, other: 'NgenAddressModel'):
        # b.address._address.subnet_of(a.address._address)
        if isinstance(other, NgenAddressModel):
            return other.address in self.address

    def __hash__(self) -> int:
        return super().__hash__()

    class Address:
        _address = None

        def __init__(self, address):
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

    class AddressIp(Address):

        def address_mask(self):
            return self._address.prefixlen

        def create_address_object(self, address: str):
            return ipaddress.ip_network(address)

        def in_range(self, other):
            return other._address > self._address

        def __str__(self):
            return self.address.exploded

    class AddressDomain(Address):

        def address_mask(self):
            return len(self.address.split('.'))

        def create_address_object(self, address):
            return address

        def in_range(self, other):
            address_set = set(self.address.split('.'))
            address_set_other = set(other.address.split('.'))

            if address_set == address_set_other:
                return True

            if address_set_other > address_set:
                return address_set & address_set_other == address_set

            return False
