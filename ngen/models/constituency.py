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
from django_dnf.fields import DomainNameField


class AbstractModelMeta(ABCMeta, type(models.Model)):
    pass


class NetworkElement(models.Model, metaclass=AbstractModelMeta):
    id = models.BigAutoField(primary_key=True)
    ip = models.GenericIPAddressField(max_length=39, blank=True, null=True)
    domain = DomainNameField(max_length=255, blank=True, null=True)
    address = None
    DOMAIN_ADDRESS: int = 1
    IPV4_ADDRESS: int = 2
    IPV6_ADDRESS: int = 3

    def guess_address_type(self, address):
        if validators.domain(address):
            return self.DOMAIN_ADDRESS
        if validators.ipv4_cidr(address):
            return self.IPV4_ADDRESS
        if validators.ipv6_cidr(address):
            return self

    @classmethod
    def create(cls, address):
        model = cls(address)
        if model.guess_address_type(address) == model.DOMAIN_ADDRESS:
            model.address = AddressDomain(address)
        elif model.guess_address_type(address) in [model.IPV4_ADDRESS, model.IPV6_ADDRESS]:
            model.address = AddressIp(address)
        else:
            raise ValueError()
        return model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.ip:
            self.address = AddressIp(self.ip)
        elif self.domain:
            self.address = AddressDomain(self.domain)

    def domain_address(self, address):
        self.domain = address
        return self.domain

    def ip_address(self, address):
        ip_address = ipaddress.ip_network(address)
        self.ip = ip_address.network_address.exploded
        self.ip_mask = ip_address.prefixlen
        return ip_address

    class Meta:
        abstract = True
        ordering = ['name']


class Host(NetworkElement):
    network = models.ForeignKey('Network', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    slug = models.CharField(max_length=100, blank=True, null=True)
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'host'


class Network(NetworkElement):
    ip_mask = models.IntegerField(blank=True, null=True)
    network_admin = models.ForeignKey('NetworkAdmin', models.DO_NOTHING, blank=True, null=True)
    network_entity = models.ForeignKey('NetworkEntity', models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    ip_start_address = models.CharField(max_length=255, blank=True, null=True)
    ip_end_address = models.CharField(max_length=255, blank=True, null=True)
    asn = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    def ip_address(self, address):
        ip_address = super().ip_address(address)
        self.ip_start_address = ip_address.network_address.exploded
        self.ip_end_address = ip_address.broadcast_address.exploded
        return ip_address

    def ip_and_mask(self):
        return "%s/%s" % (self.ip, self.ip_mask)

    class Meta:
        db_table = 'network'


class NetworkAdmin(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=100, blank=True, null=True)
    active = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'network_admin'


class NetworkEntity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    active = models.IntegerField()
    created_by = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'network_entity'


class Address(ABC):
    # _address = None

    # address_mask = None

    def __init__(self, address):
        self.address = address

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = self.create_address_object(value)

    @property
    @abstractmethod
    def address_mask(self):
        pass

    @address_mask.setter
    def address_mask(self, value):
        self._address_mask = value

    @abstractmethod
    def in_range(self, other):
        pass

    @abstractmethod
    def in_range(self, other):
        pass

    @abstractmethod
    def create_address_object(self, address):
        pass

    def __eq__(self, other):
        return self.address == other.address

    def __contains__(self, other):
        self.in_range(other)


class AddressIp(Address):

    @property
    def address(self):
        return self._address.exploded

    @property
    def address_mask(self):
        return self._address.prefixlen

    def create_address_object(self, address: str):
        return ipaddress.ip_network(address)

    def in_range(self, other: str):
        return ipaddress.ip_address(other) in self.address


class AddressDomain(Address):

    @property
    def address(self):
        return self._address

    @property
    def address_mask(self):
        return len(self.address.split('.'))

    def create_address_object(self, address):
        return address

    def in_range(self, other):
        address_set = set(self.address.split('.'))
        address_set_other = set(other.address.split('.'))

        if address_set == address_set_other:
            return True

        if address_set > address_set_other:
            return set(address_set) & set(address_set_other) == set(address_set_other)

        return False
