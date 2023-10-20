from rest_framework import serializers

from ngen.utils import slugify_underscore


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

    def to_internal_value(self, data):
        """
        Override the `to_internal_value` method to allow slugs.
        """
        try:
            # Try to get the related object using a hyperlink
            return super().to_internal_value(data)
        except serializers.ValidationError:
            # If that fails, try to get the related object using a slug
            slug = slugify_underscore(data)
            try:
                queryset = self.get_queryset()
                return queryset.get(**{self.slug_field: slug})
            except queryset.model.DoesNotExist:
                raise serializers.ValidationError(
                    f"{slug} is not a valid slug for {queryset.model.__name__}."
                )


class ConstanceValueField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data
