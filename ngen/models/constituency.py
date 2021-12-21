import ipaddress
from abc import ABC, abstractmethod

import validators
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from model_utils import Choices
from netfields import NetManager, CidrAddressField
from treebeard.al_tree import AL_Node

from .incident import NgenModel


class Network(NgenModel, AL_Node):
    id = models.BigAutoField(primary_key=True)
    cidr = CidrAddressField(null=True, unique=True)
    domain = models.CharField(max_length=255, null=True, unique=True, default=None)
    contacts = models.ManyToManyField('Contact')
    active = models.BooleanField(default=True)
    TYPE = Choices('internal', 'external')
    type = models.CharField(choices=TYPE, default=TYPE.internal, max_length=20)
    network_entity = models.ForeignKey('NetworkEntity', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True)
    objects = NetManager()
    node_order_by = ['parent', '-cidr', 'domain']
    _address = None
    DOMAIN_ADDRESS: int = 1
    IPV4_ADDRESS: int = 2
    IPV6_ADDRESS: int = 3

    def guess_address_type(self, address: str):
        if validators.domain(address) or len(address.split('.')) == 1 and len(address) == 2:
            return self.DOMAIN_ADDRESS
        ip_version = ipaddress.ip_network(address).version
        if ip_version == 4:
            return self.IPV4_ADDRESS
        if ip_version == 6:
            return self.IPV6_ADDRESS

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
        return self.address.address

    def __contains__(self, other: "Network"):
        # b.address._address.subnet_of(a.address._address)
        if isinstance(other, Network):
            return other.address in self.address

    def is_default(self):
        return self.address.address == '0.0.0.0/0'

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

    def get_ancestors_contacts(self):
        contacts = []
        for ancestor in self.get_ancestors():
            for contact in ancestor.contacts.all():
                contacts.append(contact.username)
        return contacts

    def get_contacts(self):
        contacts = []
        for contact in self.contacts.all():
            contacts.append(contact.username)
        return contacts

    class Meta:
        db_table = 'network'
        ordering = ['-cidr']


class Contact(NgenModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    public_key = models.CharField(max_length=4000, blank=True, null=True)
    TYPE = Choices('email', 'telegram', 'phone', 'uri')
    type = models.CharField(choices=TYPE, default=TYPE.email, max_length=20)
    ROLE = Choices('technical', 'administrative', 'abuse', 'notifications', 'noc')
    role = models.CharField(choices=ROLE, default=ROLE.administrative, max_length=20)
    priority = models.ForeignKey('Priority', models.DO_NOTHING, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')

    def __repr__(self):
        return self.username

    class Meta:
        db_table = 'contact'


class NetworkEntity(NgenModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    def __repr__(self):
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

    def __repr__(self):
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
