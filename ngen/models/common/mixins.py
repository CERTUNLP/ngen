import ipaddress

from auditlog.models import AuditlogHistoryField
from constance import config
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.apps import apps
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy
from django_lifecycle import (
    LifecycleModelMixin,
    hook,
    BEFORE_UPDATE,
    BEFORE_CREATE,
    BEFORE_DELETE,
)
from model_utils.models import TimeStampedModel
from netfields import NetManager, CidrAddressField
from treebeard.al_tree import AL_Node
import ngen.models
from taggit.managers import TaggableManager

import ngen
from ngen.utils import clean_list, slugify_underscore
from .parsing import StringIdentifier, StringType


class AuditModelMixin(TimeStampedModel):
    history = AuditlogHistoryField()

    class Meta:
        abstract = True


class ValidationModelMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class SlugModelMixin(ValidationModelMixin, models.Model):
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        abstract = True

    def _slug_field(self):
        return "name"

    def _slugify(self, data):
        return slugify_underscore(data)

    def slugify(self):
        return self._slugify(getattr(self, self._slug_field()))

    def clean_fields(self, exclude=None):
        self.slug = self.slugify()
        super().clean_fields(exclude=exclude)


class TreeModelMixin(AL_Node, ValidationModelMixin):
    parent = models.ForeignKey(
        "self",
        models.DO_NOTHING,
        null=True,
        blank=True,
        db_index=True,
        related_name="children",
    )

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

    def clean_fields(self, exclude=None):
        # Check loops. This is not really performant, but it works
        visited = set()
        elem = self.parent
        while elem:
            if elem.pk == self.pk or elem.pk in visited:
                raise ValidationError(
                    {
                        "parent": [
                            gettext_lazy(
                                "Parent can't be a descendant of the instance."
                            )
                        ]
                    }
                )
            visited.add(elem.pk)
            elem = elem.parent
        super().clean_fields(exclude=exclude)


class MergeModelMixin(LifecycleModelMixin, TreeModelMixin):
    class Meta:
        abstract = True

    @property
    def blocked(self) -> bool:
        raise NotImplementedError

    @property
    def blocked_fields(self) -> list[str]:
        """
        Fields that are blocked to be modified on blocked instances.
        """
        key = f"BLOCKED_FIELDS_{self.__class__.__name__.upper()}"
        values = getattr(config, key, "") or ""
        values = values.split(",")
        values += [f"{v}_id" for v in values]
        return clean_list(values)

    @property
    def allowed_fields_on_merged(self) -> list[str]:
        """
        Fields that are allowed to be modified on merged instances.
        """
        key = f"ALLOWED_FIELDS_MERGED_{self.__class__.__name__.upper()}"
        values = getattr(config, key, "") or ""
        values = values.split(",")
        values += [f"{v}_id" for v in values]
        return clean_list(values)

    @property
    def mergeable(self) -> bool:
        return not self.merged and not self.blocked

    @property
    def merged(self) -> bool:
        return self.is_child()

    def mergeable_with(self, child: "MergeModelMixin") -> bool:
        if self.uuid == child.uuid:
            raise ValidationError(
                {"parent": gettext_lazy("The parent must not be the same instance.")}
            )
        if not self.mergeable:
            raise ValidationError(
                {"parent": gettext_lazy("The parent is not mergeable or is blocked.")}
            )
        if child.blocked:
            raise ValidationError(
                {"__all__": gettext_lazy("The child is not mergeable or is blocked.")}
            )
        return True

    def reassign_children(self, other: "MergeModelMixin"):
        for child in other.children.all():
            child.parent = self
            child.save()

    def merge(self, child: "MergeModelMixin", save_child: bool = True):
        self.reassign_children(child)
        child.parent = self
        if save_child:
            # Save child only if it's not saved yet, used to avoid recursion on parent_changed
            child.save()

    @hook(BEFORE_UPDATE, when="parent", has_changed=True)
    @hook(BEFORE_CREATE, when="parent", was=None)
    def parent_changed(self):
        if self.initial_value("parent") is None:
            if (
                self.parent
                and self.parent.mergeable_with(self)
                and not self._state.adding
            ):
                self.parent.merge(self, save_child=False)
        else:
            raise ValidationError(
                {
                    "__all__": gettext_lazy(
                        "Parent of merged instances can't be modified"
                    )
                }
            )

    @hook(BEFORE_DELETE)
    def delete_children(self):
        for child in self.get_descendants():
            child.delete()

    @hook(BEFORE_UPDATE)
    def check_allowed_fields(self, exclude=None):
        if (
            self.merged and self.__class__.objects.filter(pk=self.pk).first().merged
        ):  # TODO: Avoid query
            for attr in self.__dict__:
                if attr not in self.allowed_fields_on_merged and self.has_changed(attr):
                    if (
                        attr == "cidr" and str(self.cidr) == self.initial_value("cidr")
                    ) or (attr == "sid" and self.sid == self.initial_value("sid")):
                        # cidr and sid has invalid check of has_changed
                        pass
                    else:
                        raise ValidationError(
                            {
                                "__all__": gettext_lazy(
                                    f"Merged instances can't be modified: {self}, {self.parent}, {self.children}"
                                )
                            }
                        )
        if self.blocked:
            exceptions = {}
            for attr in self.__dict__:
                if attr in self.blocked_fields and str(self.initial_value(attr)) != str(
                    getattr(self, attr)
                ):
                    if config.BLOCKED_FIELDS_EXCEPTION:
                        exceptions[attr] = [
                            {
                                "__all__": gettext_lazy(
                                    f"{attr} of blocked instances can't be modified"
                                )
                            }
                        ]
                    else:
                        self.__dict__[attr] = self.initial_value(attr)
            if exceptions:
                raise ValidationError(exceptions)


class EvidenceModelMixin(models.Model):
    evidence = GenericRelation("ngen.Evidence")
    _files = []

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        for evidence in self.evidence.all():
            evidence.delete()
        super().delete()

    def save(self, **kwargs):
        super().save()
        for file in self.files:
            self.add_evidence(file)

    def evidence_path(self):
        return f"evidence/{self.__class__.__name__}/{self.id}"

    def add_evidence(self, file):
        self.evidence.get_or_create(file=file)

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, files):
        self._files = files


class PriorityModelMixin(ValidationModelMixin, models.Model):
    priority = models.ForeignKey("Priority", models.PROTECT, null=True, blank=True)

    class Meta:
        abstract = True

    def clean_fields(self, exclude=None):
        if not self.priority:
            self.priority = ngen.models.Priority.default_priority()
        super().clean_fields(exclude=exclude)


class AddressManager(NetManager):
    def cidr_parents_of(self, cidr: str, queryset=None):
        return (
            self._qs(queryset)
            .filter(cidr__net_contains_or_equals=cidr)
            .order_by("-cidr")
        )

    def domain_parents_of(self, domain: str, queryset=None):
        query = Q(domain="*") | Q(domain=domain)
        partition = domain.partition(".")[-1]
        while partition:
            query |= Q(domain=partition)
            partition = partition.partition(".")[-1]
        return self._qs(queryset).filter(query).order_by(Length("domain").desc())

    def parents_of(self, address: "AddressModelMixin", queryset=None):
        if address.cidr:
            return self.cidr_parents_of(str(address.address), queryset)
        elif address.domain:
            print(address, address.domain, address.address)
            return self.domain_parents_of(str(address.address), queryset)
        return self.none()

    def parents_of_many(self, addresses: list["AddressModelMixin"], queryset=None):
        parents = self.none()
        for address in addresses:
            parents |= self.parents_of(address, queryset)
        return parents

    def parent_of(self, address: "AddressModelMixin"):
        return self.parents_of(address)

    def cidr_children_of(self, cidr: str, queryset=None):
        return (
            self._qs(queryset)
            .filter(cidr__net_contained_or_equal=cidr)
            .order_by("cidr")
        )

    def domain_children_of(self, domain: str, queryset=None):
        return (
            self._qs(queryset)
            .filter(domain__endswith=domain)
            .order_by(Length("domain").desc())
        )

    def children_of(self, address: "AddressModelMixin", queryset=None):
        if address.cidr:
            return self.cidr_children_of(str(address.address), queryset)
        elif address.domain:
            return self.domain_children_of(str(address.address), queryset)
        return self.none()

    def children_of_by_string(self, address: str, queryset=None):
        network = ngen.models.Network(address_value=address)
        if network.address:
            return self.children_of(network, queryset)
        return self.none()

    def children_of_cidr(self, cidr: str, queryset=None):
        return self.cidr_children_of(cidr, queryset)

    def children_of_domain(self, domain: str, queryset=None):
        return self.domain_children_of(domain, queryset)

    # def children_of_cidr_or_domain(self, cidr: str, domain: str):
    #     if cidr:
    #         return self.cidr_children_of(cidr)
    #     elif domain:
    #         return self.domain_children_of(domain)
    #     return self.none()
    #
    def children_of_cidr_or_domain(self, cidr: str, domain: str, queryset=None):
        return self.children_of_cidr(cidr, queryset) | self.children_of_domain(
            domain, queryset
        )

    def defaults(self, queryset=None):
        return self._qs(queryset).filter(Q(cidr__prefixlen=0) | Q(domain="*"))

    def defaults_ipv4(self, queryset=None):
        return self._qs(queryset).filter(cidr__prefixlen=0, cidr__family=4)

    def defaults_ipv6(self, queryset=None):
        return self._qs(queryset).filter(cidr__prefixlen=0, cidr__family=6)

    def defaults_domain(self, queryset=None):
        return self._qs(queryset).filter(domain="*")

    def _qs(self, queryset=None):
        return queryset or self


class AddressModelMixin(ValidationModelMixin, models.Model):
    cidr = CidrAddressField(null=True, default=None, blank=True)
    domain = models.CharField(max_length=255, null=True, default=None, blank=True)
    address_value = models.CharField(max_length=255, null=False, default="", blank=True)
    objects = AddressManager()
    address = None
    sid = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assign_address()

    def assign_address(self):
        if self.address_value:
            self.sid = StringIdentifier(self.address_value)
            if self.sid.network_type == StringType.CIDR:
                self.cidr = self.sid.parsed_string
            elif self.sid.network_type == StringType.DOMAIN:
                self.domain = self.sid.parsed_string

        if self.cidr:
            try:
                self.address = self.AddressIpv4(self.cidr)
            except ValueError:
                self.address = self.AddressIpv6(self.cidr)
            self.cidr = self.address.sanitized()
            return self.address
        elif self.domain:
            self.address = self.AddressDomain(self.domain)
            self.domain = self.address.sanitized()
            return self.address
        return None

    def validate_addresses(self):
        if not self.address_value and not self.cidr and not self.domain:
            msg = "At least cidr or domain must be setted"
            raise ValidationError({"cidr": [msg], "domain": [msg]})
        elif self.cidr and self.domain:
            msg = "cidr and domain are mutually exclusive"
            raise ValidationError(
                {"address_value": [msg], "cidr": [msg], "domain": [msg]}
            )

        if self.address_value:
            self.sid = StringIdentifier(self.address_value)
            if self.cidr:
                if ipaddress.ip_network(self.cidr) != self.sid.parsed_obj:
                    msg = "cidr is not in address_value"
                    raise ValidationError({"cidr": [msg], "address_value": [msg]})
            elif self.domain:
                if not self.domain == self.sid.parsed_string:
                    msg = "domain is not in address_value"
                    raise ValidationError({"domain": [msg], "address_value": [msg]})

    def clean_fields(self, exclude=None):
        # Reassign address_value to cidr/domain to validate it
        if not self.assign_address():
            raise ValidationError(
                gettext_lazy("Address must be either a CIDR or a domain")
            )

        # Validate address_value - cidr/domain consistency
        self.validate_addresses()

        if not self.address.is_valid():
            raise ValidationError(
                {self.field_name(): [f"Must be a valid {self.field_name()}"]}
            )
        super().clean_fields(exclude=exclude)

    def __eq__(self, other: "AddressModelMixin"):
        if isinstance(other, AddressModelMixin):
            return self.address == other.address

    def __str__(self):
        return self.address.network_string()

    def __contains__(self, other: "AddressModelMixin"):
        # b.address._address.subnet_of(a.address._address)
        if isinstance(other, AddressModelMixin):
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
            return "cidr"

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
            return "0.0.0.0/0"

    class AddressIpv6(AddressIp):

        def create_address_object(self, address: str):
            return ipaddress.IPv6Network(address)

        def is_ipv4(self):
            return False

        def is_ipv6(self):
            return True

        def default(self):
            return "::/0"

    class AddressDomain(Address):

        def address_mask(self):
            if self.address in ["*", "."]:
                return 0
            return len(self.address.split("."))

        def create_address_object(self, address):
            # return address.replace('*','').strip().lower().split('/')[0]
            a = address.replace("*", "").strip().strip(".").lower().split("/")[0]
            if a == "":
                return "*"
            return a

        def in_range(self, other):
            address_set = set(self.address.split("."))
            address_set_other = set(other.address.split("."))

            if address_set == address_set_other:
                return True

            if address_set_other > address_set:
                return address_set & address_set_other == address_set

            return False

        def default(self):
            return "*"

        def field_name(self):
            return "domain"

        def sanitized(self):
            return self.create_address_object(self.address)

        def network_string(self):
            if self.is_default():
                return "*"
            return f"{self.address}"

        def network_with_mask(self):
            return f"{self.address}/{self.address_mask()}"

        def is_valid(self):
            return self.address == "*" or StringIdentifier.match_regex(
                StringType.DOMAIN, self.address
            )

        def network_address(self):
            return self.address

        # def __str__(self):
        # if self.is_default():
        #     return '*/0'
        # return f'{self.address}/{self.address_mask()}'


class ArtifactRelatedMixin(models.Model):
    artifact_relation = GenericRelation(
        "ngen.ArtifactRelation", related_query_name="%(class)ss"
    )

    class Meta:
        abstract = True

    @property
    def enrichable(self):
        return True

    @property
    def artifacts(self):
        return ngen.models.Artifact.objects.filter(
            artifact_relation__in=self.artifact_relation.all()
        ).order_by("id")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.artifact_update()

    def artifact_update(self):
        """
        Update or create new artifacts and relations for the instance
        based on the artifacts_dict property of the instance.
        """
        if self.enrichable:
            artifact_types = config.ALLOWED_ARTIFACTS_TYPES or ""
            for artifact_type, artifact_values in self.artifacts_dict.items():
                if artifact_type in artifact_types.split(","):
                    relations = []
                    for artifact_value in artifact_values:
                        artifact, created = ngen.models.Artifact.objects.get_or_create(
                            value=artifact_value, defaults={"type": artifact_type}
                        )
                        relation, rel_created = (
                            ngen.models.ArtifactRelation.objects.get_or_create(
                                artifact=artifact,
                                content_type=ContentType.objects.get_for_model(self),
                                object_id=self.id,
                                defaults={"auto_created": True},
                            )
                        )
                        relations.append(relation)
                        if not created:
                            artifact.enrich()
                    # Delete auto_created relations that are not in the new list
                    self.artifact_relation.filter(auto_created=True).exclude(
                        pk__in=[relation.pk for relation in relations]
                    ).delete()

    @property
    def artifacts_dict(self) -> dict[str, list]:
        raise NotImplementedError


class ChannelableMixin(models.Model):
    """
    Mixin for models that have Communication Channels
    """

    communication_channels = GenericRelation(
        "ngen.CommunicationChannel", related_name="communication_channels"
    )

    class Meta:
        abstract = True

    def get_team_and_assigned_contacts(self):
        raise NotImplementedError

    def get_affected_contacts(self):
        raise NotImplementedError

    def get_reporter_contacts(self):
        raise NotImplementedError


# class TaggedItemMixin(models.Model):

#     tags = TaggableManager(through=apps.get_model("ngen", "TaggedItem"))

#     class Meta:
#         abstract = True
