from django.test import TestCase
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from ngen.models import Artifact, ArtifactRelation, Event, Taxonomy, Feed, Tlp, Priority, User
from django.utils import timezone
from datetime import timedelta
from django.db.utils import IntegrityError
from psycopg2.errors import UniqueViolation


class TestArtifact(TestCase):
    """
    This will handle Artifact testcases
    """

    def test_create_artifact(self):
        """
        This will handle Artifact creation test
        """
        artifact = Artifact.objects.create(type=Artifact.TYPE.ip, value="192.168.1.1")
        self.assertEqual(artifact.type, Artifact.TYPE.ip)
        self.assertEqual(artifact.value, "192.168.1.1")

    def test_str_method(self):
        artifact = Artifact.objects.create(type=Artifact.TYPE.ip, value="192.168.1.1")
        self.assertEqual(str(artifact), "ip: 192.168.1.1")

    def test_unique_constraint(self):
        # Ensure that creating an artifact with a duplicate value raises a ValidationError
        Artifact.objects.create(type=Artifact.TYPE.ip, value="192.168.1.1")
        with self.assertRaises(IntegrityError):
            Artifact.objects.create(type=Artifact.TYPE.ip, value="192.168.1.1")


class TestArtifactRelation(TestCase):
    """
    This will handle Artifact Relation testcases
    """

    def setUp(self):
        self.artifact = Artifact.objects.create(type=Artifact.TYPE.ip, value="192.168.1.1")
        self.taxonomy = Taxonomy.objects.create(
            type="incident", name="Phising", slug="phising"
        )
        self.feed = Feed.objects.create(slug="shodan", name="Shodan")
        self.tlp = Tlp.objects.create(
            slug="white",
            when="Given some circumstance",
            why="Some reason",
            information="Some information",
            description="Some description",
            name="White",
            code=0,
        )
        self.priority = Priority.objects.create(name="Medium", severity=3)
        self.user = User.objects.create(
            username="test", password="test", priority=self.priority
        )
        self.event = Event.objects.create(
            domain="info.unlp.edu.ar",
            taxonomy=self.taxonomy,
            feed=self.feed,
            tlp=self.tlp,
            reporter=self.user,
            notes="Some notes",
            priority=self.priority,
        )

    def test_create_artifact_relation(self):
        """
        This will handle Artifact relation testing
        """

        # Access the 'id' attribute of the created event to get its ID
        self.event_id = self.event.id

        # Create the ArtifactRelation
        relation = ArtifactRelation.objects.create(
            artifact=self.artifact,
            content_type=ContentType.objects.get_for_model(Event),
            object_id=self.event_id
        )
        self.assertEqual(relation.artifact, self.artifact)

    def test_relation_deletion_on_object_deletion(self):
        """
        Test that the Relation gets deleted if the object gets deleted.
        """
        relation = ArtifactRelation.objects.create(
            artifact=self.artifact,
            content_type=ContentType.objects.get_for_model(Event),
            object_id=self.event.id
        )

        self.assertTrue(ArtifactRelation.objects.filter(artifact=self.artifact).exists())

        # Delete the event
        self.event.delete()

        # Ensure that the relation is removed after the event deletion
        self.assertFalse(ArtifactRelation.objects.filter(artifact=self.artifact).exists())

    def test_relation_deletion_on_artifact_deletion(self):
        """
        Test that the Relation gets deleted if the artifact gets deleted.
        """
        # Create the ArtifactRelation
        relation = ArtifactRelation.objects.create(
            artifact=self.artifact,
            content_type=ContentType.objects.get_for_model(Event),
            object_id=self.event.id
        )

        # Ensure that the relation exists
        self.assertTrue(ArtifactRelation.objects.filter(artifact=self.artifact).exists())

        # Delete the artifact
        self.artifact.delete()

        # Ensure that the relation is removed after the artifact deletion
        self.assertFalse(ArtifactRelation.objects.filter(artifact=self.artifact).exists())

    def test_artifact_without_connections_deletion(self):
        """
        Test that the artifact gets deleted if it doesn't have any connections.
        """
        # Create the ArtifactRelation
        relation = ArtifactRelation.objects.create(
            artifact=self.artifact,
            content_type=ContentType.objects.get_for_model(Event),
            object_id=self.event.id
        )

        # Ensure that the relation exists
        self.assertTrue(ArtifactRelation.objects.filter(artifact=self.artifact).exists())

        # Delete the event
        self.event.delete()

        # Ensure that the relation is removed after the event deletion
        self.assertFalse(ArtifactRelation.objects.filter(artifact=self.artifact).exists())

        # Ensure that the artifact is deleted
        self.assertFalse(Artifact.objects.filter(pk=self.artifact.pk).exists())
