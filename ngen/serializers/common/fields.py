from rest_framework import serializers

from ngen.utils import slugify_underscore
from ngen.models import Taxonomy, TaxonomyGroup


class GenericRelationField(serializers.RelatedField):
    def to_internal_value(self, data):
        pass

    def to_representation(self, related_list):
        return self.generic_detail_links(related_list)

    # def generic_detail_link(self, related, request=None):
    #     return self.generic_detail_link(related, request)

    def generic_detail_links(self, related_list, request=None):
        return [self.generic_detail_link(related, request) for related in related_list]

    def generic_detail_link(self, related, request=None):
        view_name = related.__class__.__name__.lower() + '-detail'
        serializer = serializers.HyperlinkedIdentityField(view_name=view_name)
        return serializer.get_url(obj=related, view_name=view_name,
                                  request=self.context.get('request', request),
                                  format=None)


class SlugOrHyperlinkedRelatedField(serializers.HyperlinkedRelatedField):
    """
    A custom field to allow creation of related objects using either a slug or
    hyperlink.
    """

    def __init__(self, **kwargs):
        self.slug_field = kwargs.pop('slug_field', 'slug')
        super().__init__(**kwargs)

    def when_invalid_slug(self, queryset, data, slug):
        raise serializers.ValidationError(f"{slug} is not a valid slug for {queryset.model.__name__}.")

    def sluglify(self, data):
        return slugify_underscore(data)

    def to_internal_value(self, data):
        """
        Override the `to_internal_value` method to allow slugs.
        """
        try:
            # Try to get the related object using a hyperlink
            return super().to_internal_value(data)
        except serializers.ValidationError:
            # If that fails, try to get the related object using a slug
            slug = self.sluglify(data)
            queryset = self.get_queryset()
            try:
                return queryset.get(**{self.slug_field: slug})
            except queryset.model.DoesNotExist:
                return self.when_invalid_slug(queryset, data, slug)


class TaxonomySlugOrHyperlinkedRelatedField(SlugOrHyperlinkedRelatedField):
    """
    A custom field to allow creation of related objects using either a slug, hyperlink, or alias.
    """

    def sluglify(self, data):
        p0, *parts = data.split('-')
        if len(parts) == 0:
            # add prefix internal: to the slug
            return f'{slugify_underscore(p0)}'
        return f'{slugify_underscore(p0)}-{slugify_underscore("_".join(parts))}'

    def when_invalid_slug(self, queryset, data, slug):
        if '-' in slug:
            group_name, taxonomy_name = slug.split("-")
            tax_group = TaxonomyGroup.objects.get_or_create(
                slug=group_name,
                defaults={
                    'name': group_name,
                    'description': 'Auto-generated group.'
                }
            )[0]
            internal_taxonomy = queryset.filter(slug=taxonomy_name).first()
        else:
            tax_group = None
            taxonomy_name = slug
            internal_taxonomy = None


        obj = queryset.create(
            name=data,
            alias_of=internal_taxonomy,
            group=tax_group,
            description='Auto-generated alias.'
        )

        return obj


class ConstanceValueField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data
