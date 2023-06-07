from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy
from django.core.exceptions import ValidationError
from model_utils import Choices

from .utils import NgenModel, NgenTreeModel, NgenPriorityMixin, NgenAddressModel, AddressManager


class NetworkManager(AddressManager):
    def parent_of(self, network: 'Network'):
        parent = super().parent_of(network)
        if not parent:
            parent = self.default_network()
        return parent

    def default_network(self):
        return self.get(cidr='0.0.0.0/0')

    def children_of(self, network: 'Network'):
        children = None
        if network.cidr:
            children = network.parent.get_children().filter(cidr__net_contained=str(network.cidr))
        elif network.domain:
            children = network.parent.get_children().filter(domain__endswith=network.domain).exclude(
                domain=network.domain)
        return children


class Network(NgenModel, NgenTreeModel, NgenAddressModel):
    contacts = models.ManyToManyField('ngen.Contact')
    active = models.BooleanField(default=True)
    TYPE = Choices(('internal', gettext_lazy('Internal')), ('external', gettext_lazy('External')))
    type = models.CharField(choices=TYPE, default=TYPE.internal, max_length=20)
    network_entity = models.ForeignKey('ngen.NetworkEntity', models.DO_NOTHING, null=True, related_name='networks')
    objects = NetworkManager()
    node_order_by = ['parent', '-cidr', 'domain']

    class Meta:
        db_table = 'network'
        ordering = ['-cidr']

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

    def clean(self):
        # cannot be setted parent by user
        self.parent = None
        if not self.cidr and not self.domain:
            raise ValidationError({'cidr': ['CIDR or Domain is required'], 'domain': ['CIDR or Domain is required']})
        if self.cidr and self.domain:
            raise ValidationError({'cidr': ['CIDR and Domain are mutually exclusive'], 'domain': ['CIDR and Domain are mutually exclusive']})

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        qs = self.__class__.objects.filter(cidr=self.cidr, domain=self.domain).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError('CIDR, Domain tuple must be unique')

    def save(self, *args, **kwargs):
        self.full_clean()
        children = None
        if not self.is_default():
            if self.get_children():
                self.get_children().update(parent=self.parent)

            self.parent = Network.objects.parent_of(self)
            children = Network.objects.children_of(self)

        super(Network, self).save(*args, **kwargs)

        if children:
            children.update(parent=self)

    def ancestors_email_contacts(self, priority):
        return self.get_ancestors_related(
            lambda obj: obj.contacts.filter(type='email').filter(priority__severity__gte=priority))

    def email_contacts(self, priority):
        return self.contacts.filter(type='email').filter(priority__severity__gte=priority)


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
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name).replace('-', '_')
        super(NetworkEntity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'network_entity'
