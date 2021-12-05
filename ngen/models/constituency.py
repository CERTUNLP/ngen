# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import ipaddress
from abc import ABCMeta, ABC, abstractmethod

import validators
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from model_utils import Choices
from netfields import NetManager, CidrAddressField
from treebeard.al_tree import AL_Node

from .incident import NgenModel


class AbstractModelMeta(ABCMeta, type(models.Model)):
    pass


class Network(NgenModel, AL_Node):
    id = models.BigAutoField(primary_key=True)
    cidr = CidrAddressField(null=True, unique=True)
    domain = models.CharField(max_length=255, null=True, unique=True, default=None)
    network_admin = models.ForeignKey('NetworkAdmin', models.DO_NOTHING, blank=True, null=True)
    network_entity = models.ForeignKey('NetworkEntity', models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(default=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, null=True, db_index=True)
    node_order_by = ['parent', '-cidr', 'domain']
    _address = None
    DOMAIN_ADDRESS: int = 1
    IPV4_ADDRESS: int = 2
    IPV6_ADDRESS: int = 3
    objects = NetManager()

    def guess_address_type(self, address: str):
        if validators.domain(address):
            return self.DOMAIN_ADDRESS
        if validators.ipv4_cidr(address):
            return self.IPV4_ADDRESS
        if validators.ipv6_cidr(address):
            return self.IPV6_ADDRESS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.cidr:
            if isinstance(self.cidr, str):
                self.address = self.cidr
            else:
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

    class Meta:
        db_table = 'network'
        ordering = ['-cidr']


class NetworkAdmin(NgenModel):
    # ROLE = Choices('technical', 'administrative', 'abuse', 'notifications', 'noc')
    # role = models.CharField(choices=ROLE, default=ROLE.administrative, max_length=20)
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'network_admin'


class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    encryption_key = models.CharField(max_length=4000, blank=True, null=True)
    network_admin = models.ForeignKey('NetworkAdmin', models.CASCADE, blank=True, null=True)
    TYPE = Choices('email', 'telegram', 'phone')
    contact_type = models.CharField(choices=TYPE, default=TYPE.email, max_length=20)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True, related_name='+')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    priority = models.ForeignKey('IncidentPriority', models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'contact'


class NetworkEntity(NgenModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

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


class AddressIp(Address):

    @Address.address.getter
    def address(self):
        return self._address.exploded

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
