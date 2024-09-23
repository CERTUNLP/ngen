from django.db import models


class CustomPermissionSupport(models.Model):
    """
    This model is used to define custom permissions for the application.

    May you need this when view does not hinerit from any type of a
    ModelViewSet class and you need to define custom permissions.

    Take into account that this model is not a table in the database, it is
    used to define custom permissions for the application.

    Avoid duplicating permissions, use the same permission name in all models
    that require the same permission.

    To apply the permissions to database run the following commands:
    $ python manage.py makemigrations
    $ python manage.py migrate

    """

    class Meta:

        managed = False  # No database table creation or deletion  \
        # operations will be performed for this model.

        default_permissions = ()  # disable "add", "change", "delete"
        # and "view" default permissions

        permissions = (
            ("view_dashboard", "View Dashboard"),
            ("view_minified_feed", "View Minified Feed"),
            ("view_minified_tlp", "View Minified TLP"),
            ("view_minified_priority", "View Minified Priority"),
            ("view_minified_artifact", "View Minified Artifact"),
            ("view_minified_user", "View Minified User"),
            ("view_minified_case", "View Minified Case"),
            ("view_minified_entity", "View Minified Entity"),
            ("view_minified_contact", "View Minified Contact"),
            ("view_minified_state", "View Minified State"),
            ("view_minified_taxonomy", "View Minified Taxonomy"),
            ("view_minified_taxonomygroup", "View Minified TaxonomyGroup"),
        )
