from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy
from model_utils import Choices

from ngen.models.common.mixins import AuditModelMixin, PriorityModelMixin, AddressModelMixin, TreeModelMixin
from .common.mixins import AddressManager


class NetworkManager(AddressManager):
    def default_network(self, network):
        """
        Return the default network for the given network type, based on the field_name and default value of the network.
        """
        return self.filter(**{network.field_name(): network.default()})

    def children_of(self, network: 'Network'):
        """
        Return all networks that are children of the given network. Not necessarily already assigned to the network.
        """
        children = None
        if network.cidr:
            children = self.filter(cidr__net_contained=str(network.cidr))
        elif network.domain != None:
            children = self.filter(domain__endswith=network.domain).exclude(domain=network.domain)
        return children

    def default_ipv4(self):
        return self.defaults_ipv4()[:1]

    def default_ipv6(self):
        return self.defaults_ipv6()[:1]

    def default_domain(self):
        return self.defaults_domain()[:1]


class Network(AuditModelMixin, TreeModelMixin, AddressModelMixin):
    contacts = models.ManyToManyField('ngen.Contact', blank=True)
    active = models.BooleanField(default=True)
    TYPE = Choices(('internal', gettext_lazy('Internal')), ('external', gettext_lazy('External')))
    type = models.CharField(choices=TYPE, default=TYPE.internal, max_length=20)
    network_entity = models.ForeignKey('ngen.NetworkEntity', models.SET_NULL, null=True, blank=True,
                                       related_name='networks')
    objects = NetworkManager()
    node_order_by = ['parent', '-cidr', 'domain']

    class Meta:
        db_table = 'network'
        ordering = ['-cidr']

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

    def clean(self):
        super().clean()
        if not self._state.adding:
            # Is not new. Needed by django admin because it validates with None object
            self.get_children().update(parent=self.parent)
        self.parent = Network.objects.parent_of(self).exclude(pk=self.pk).first()

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        if self.address:
            fn = self.field_name()
            qs = self.__class__.objects.filter(**{fn: self.address}).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({f'{fn}': [f'Already exists a network with this {fn}']})
        else:
            raise ValidationError({'__all__': [f'Network must have a valid address (cidr/domain)']})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Network.objects.children_of(self).update(parent=self)

    def ancestors_email_contacts(self, priority):
        return self.get_ancestors_related(
            lambda obj: obj.contacts.filter(type='email').filter(priority__severity__gte=priority))

    def email_contacts(self, priority):
        return self.contacts.filter(type='email').filter(priority__severity__gte=priority)


class Contact(AuditModelMixin, PriorityModelMixin):
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

    def __init__(self, *args, **kwargs):
        super(Contact, self).__init__(*args, **kwargs)

    def __str__(self):
        return "%s (%s)" % (self.username, self.role)

    class Meta:
        db_table = 'contact'
        ordering = ['username']


class NetworkEntity(AuditModelMixin):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(NetworkEntity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'network_entity'
