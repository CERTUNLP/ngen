from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from django.utils.text import slugify
from django.utils.translation import gettext_lazy
from model_utils import Choices
from netfields import NetManager

from .utils import NgenModel, NgenTreeModel, NgenPriorityMixin, NgenAddressModel


class Network(NgenModel, NgenTreeModel, NgenAddressModel):
    contacts = models.ManyToManyField('ngen.Contact')
    active = models.BooleanField(default=True)
    TYPE = Choices(('internal', gettext_lazy('Internal')), ('external', gettext_lazy('External')))
    type = models.CharField(choices=TYPE, default=TYPE.internal, max_length=20)
    network_entity = models.ForeignKey('ngen.NetworkEntity', models.DO_NOTHING, null=True)
    objects = NetManager()
    node_order_by = ['parent', '-cidr', 'domain']

    class Meta:
        db_table = 'network'
        ordering = ['-cidr']
        unique_together = ['cidr', 'domain']

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
            children = Network.lookup_children(self)

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
    def lookup_children(cls, network):
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
