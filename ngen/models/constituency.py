import ipaddress
from abc import ABC, abstractmethod

import validators
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from django.utils.text import slugify
from django.utils.translation import gettext_lazy
from model_utils import Choices
from netfields import NetManager, CidrAddressField
from tld import is_tld

from .utils import NgenModel, NgenTreeModel, NgenPriorityMixin


class Network(NgenModel, NgenTreeModel):
    cidr = CidrAddressField(null=True, unique=True)
    domain = models.CharField(max_length=255, null=True, unique=True, default=None)
    contacts = models.ManyToManyField('ngen.Contact')
    active = models.BooleanField(default=True)
    TYPE = Choices(('internal', gettext_lazy('Internal')), ('external', gettext_lazy('External')))
    type = models.CharField(choices=TYPE, default=TYPE.internal, max_length=20)
    network_entity = models.ForeignKey('ngen.NetworkEntity', models.DO_NOTHING, null=True)
    objects = NetManager()
    node_order_by = ['parent', '-cidr', 'domain']
    _address = None
    DOMAIN_ADDRESS: int = 1
    IPV4_ADDRESS: int = 2
    IPV6_ADDRESS: int = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.cidr:
            if isinstance(self.cidr, str):
                self.cidr = ipaddress.ip_network(self.cidr)
            self.address = self.cidr.exploded
        elif self.domain:
            self.address = self.domain

    @classmethod
    def create(cls, address: str):
        model = cls(address)
        model.address = address
        return model

    @property
    def address(self) -> "Address":
        return self._address

    def guess_address_type(self, address: str):
        if validators.domain(address) or is_tld(address):
            return self.DOMAIN_ADDRESS
        ip_version = ipaddress.ip_network(address).version
        if ip_version == 4:
            return self.IPV4_ADDRESS
        if ip_version == 6:
            return self.IPV6_ADDRESS

    @address.setter
    def address(self, value: str):
        if self.guess_address_type(value) == self.DOMAIN_ADDRESS:
            self._address = AddressDomain(value)
            self.domain = self.address.address
        elif self.guess_address_type(value) in [self.IPV4_ADDRESS, self.IPV6_ADDRESS]:
            self._address = AddressIp(value)
            self.cidr = self.address.address
        else:
            raise ValueError()

    def __eq__(self, other: "Network"):
        if isinstance(other, Network):
            return self.address == other.address

    def __repr__(self):
        return self.address.__repr__()

    def __str__(self):
        return self.address.__str__()

    def __contains__(self, other: "Network"):
        # b.address._address.subnet_of(a.address._address)
        if isinstance(other, Network):
            return other.address in self.address

    def is_default(self):
        return self.domain == ''

    @classmethod
    def find_problems(cls):
        pass

    @classmethod
    def fix_tree(cls):
        for network in Network.objects.exclude(cidr__endswith='32').exclude(cidr='0.0.0.0/0').order_by('cidr'):
            network.save()

    def delete(self):
        if self.get_children():
            self.get_children().update(parent=self.parent)
        super(Network, self).delete()

    def save(self, *args, **kwargs):
        children = None
        if not self.is_default():
            if self.get_children():
                self.get_children().update(parent=self.parent)

            self.parent = Network.lookup_parent(self)
            children = Network.lookup_parent_children(self)

        super(Network, self).save(*args, **kwargs)

        if children:
            children.update(parent=self)

    @classmethod
    def lookup_parent(cls, network):
        parent = None
        if network.cidr:
            parent = Network.objects.filter(cidr__net_contains=network.cidr.exploded).order_by('-cidr').first()
            if not parent:
                parent = Network.lookup_default_network()
        elif network.domain:
            query = Q(domain='')
            partition = network.domain.partition('.')[-1]
            while partition:
                query |= Q(domain=partition)
                partition = partition.partition('.')[-1]
            parent = Network.objects.filter(query).order_by(Length('domain').desc()).first()
        return parent

    @classmethod
    def lookup_parent_children(cls, network):
        children = None
        if network.cidr:
            children = network.parent.get_children().filter(cidr__net_contained=network.cidr.exploded)
        elif network.domain:
            children = network.parent.get_children().filter(domain__endswith=network.domain).exclude(
                domain=network.domain)
        return children

    @classmethod
    def lookup_default_network(cls):
        return cls.objects.get(cidr='0.0.0.0/0')

    def ancestors_email_contacts(self, priority):
        return self.get_ancestors_related(
            lambda obj: obj.contacts.filter(type='email').filter(priority__severity__gte=priority))

    def email_contacts(self, priority):
        return self.contacts.filter(type='email').filter(priority__severity__gte=priority)

    class Meta:
        db_table = 'network'
        ordering = ['-cidr']


class Contact(NgenModel, NgenPriorityMixin):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    public_key = models.CharField(max_length=4000, null=True)
    TYPE = Choices(('email', gettext_lazy('Email')), ('telegram', gettext_lazy('Telegram')),
                   ('phone', gettext_lazy('Phone')), ('uri', gettext_lazy('URI')))
    type = models.CharField(choices=TYPE, default=TYPE.email, max_length=20)
    ROLE = Choices(('technical', gettext_lazy('Technical')), ('administrative', gettext_lazy('Administrative')),
                   ('abuse', gettext_lazy('Abuse')), ('notifications', gettext_lazy('Notifications')),
                   ('noc', gettext_lazy('NOC')))
    role = models.CharField(choices=ROLE, default=ROLE.administrative, max_length=20)

    def __str__(self):
        return "%s (%s)" % (self.username, self.role)

    class Meta:
        db_table = 'contact'
        ordering = ['username']


class NetworkEntity(NgenModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    active = models.IntegerField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(NetworkEntity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'network_entity'


class Address(ABC):
    _address = None

    def __init__(self, address):
        self.address = address

    @property
    @abstractmethod
    def address(self):
        pass

    @address.setter
    def address(self, value):
        self._address = self.create_address_object(value)

    @abstractmethod
    def address_mask(self):
        pass

    @abstractmethod
    def in_range(self, other):
        pass

    @abstractmethod
    def create_address_object(self, address):
        pass

    def __eq__(self, other: "Address"):
        return self.address == other.address

    def __contains__(self, other: "Address"):
        return self.in_range(other)

    def __str__(self):
        return self.address


class AddressIp(Address):

    @Address.address.getter
    def address(self):
        return self._address

    def address_mask(self):
        return self._address.prefixlen

    def create_address_object(self, address: str):
        return ipaddress.ip_network(address)

    def in_range(self, other: Address):
        return other._address > self._address

    def __str__(self):
        return self.address.exploded


class AddressDomain(Address):
    @Address.address.getter
    def address(self) -> str:
        return self._address

    def address_mask(self: Address):
        return len(self.address.split('.'))

    def create_address_object(self, address):
        return address

    def in_range(self: Address, other: Address):
        address_set = set(self.address.split('.'))
        address_set_other = set(other.address.split('.'))

        if address_set == address_set_other:
            return True

        if address_set_other > address_set:
            return address_set & address_set_other == address_set

        return False
