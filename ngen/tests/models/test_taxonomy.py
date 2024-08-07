from django.core.exceptions import ValidationError
from django.test import TestCase

from ngen.models import Taxonomy, TaxonomyGroup


class TaxonomyTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ 
        Create instances of Taxonomy
        """
        cls.parent = Taxonomy.objects.create(type='vulnerability', name='Parent')
        cls.child1 = Taxonomy.objects.create(type='vulnerability', name='Child 1', parent=cls.parent)
        cls.child2 = Taxonomy.objects.create(type='vulnerability', name='Child 2', parent=cls.child1)
        cls.aRootNode = Taxonomy.objects.create(type='vulnerability', name='A Root Node')
        cls.aNode_Parent = Taxonomy.objects.create(type='vulnerability', name='A Node Parent')
        cls.aNode = Taxonomy.objects.create(type='vulnerability', name='a Node', parent=cls.aNode_Parent)
        cls.aNode_child1 = Taxonomy.objects.create(type='vulnerability', name='Node Child 1', parent=cls.aNode)
        cls.aNode_child2 = Taxonomy.objects.create(type='vulnerability', name='Node Child 2', parent=cls.aNode)
        cls.aNode_child3 = Taxonomy.objects.create(type='vulnerability', name='Node Child 3', alias_of=cls.aNode)
        cls.aNode_child4 = Taxonomy.objects.create(type='vulnerability', name='Node Child 4', alias_of=cls.child1)

        cls.taxonomy_group2 = TaxonomyGroup.objects.create(name='Shadowserver')
        cls.parent2 = Taxonomy.objects.create(type='incident', name='Parent2', group=cls.taxonomy_group2)
        cls.p2_child1 = Taxonomy.objects.create(type='incident', name='P2 Child 1', parent=cls.parent2)
        cls.p2_child2 = Taxonomy.objects.create(type='incident', name='P2 Child 2', parent=cls.parent2)
        cls.p2_child1_child1 = Taxonomy.objects.create(type='incident', name='P2 Child 1 Child 1',
                                                       parent=cls.p2_child1, alias_of=cls.aNode_child2)

        # self.aNode = Taxonomy.objects.create(type='vulnerability' name= 'Node')

    # def test_duplicated_taxonomy(self):
    #     """
    #     Test that taxonomies are not duplicated. This test does not work because slugs unique key constraint is preventing
    #     a taxonomy with same name and different slug to exist.
    #     """
    #     with self.assertRaises(UniqueViolation):
    #         # Create taxonomies with the same name and different slugs
    #         taxonomy1 = Taxonomy.objects.create(type='vulnerability', name='Ejemplo', slug='parent-test-1')
    #         taxonomy2 = Taxonomy.objects.create(type='vulnerability', name='Ejemplo', slug='parent-test-2')

    # def test_unique_slug_creation(self):
    #     """
    #     Test: Slugs are created correctly and are unique. Can't create two slugs with the same name.
    #     """
    #     with self.assertRaises(UniqueViolation):
    #         # Create taxonomies with the same slugs
    #         Slug1 = Taxonomy.objects.create(type='vulnerability', name="Test Name", slug="slug1")
    #         Slug2 = Taxonomy.objects.create(type='incident', name="Test Name2", slug="slug1")

    def test_node_deletion(self):
        """
        Test: Simple deletion
        """
        self.aNode.delete()  # Delete aNode
        deleted_node = Taxonomy.objects.filter(id=self.aNode.id).first()  # Check for deleted node ID in the DB
        self.assertIsNone(deleted_node)

    def test_parent_deletion(self):
        """
        Test: If a root parent is deleted, all children must NOT have a parent
        """
        children_queryset = self.aRootNode.get_children()  # Getting children from Root before deletion

        # Convert the queryset to a list or other data structure
        children = list(children_queryset)

        self.aRootNode.delete()  # Delete Root

        # Children should not have any parents
        for child in children:
            child.refresh_from_db()  # Refresh the child object from the database
            self.assertIsNone(child.parent)

    def test_middle_node_deletion(self):
        """
        Test: If a middle node is deleted, parent and children should be connected
        """
        # Saving
        parent_node = self.aNode.get_parent()
        children_queryset = self.aNode.get_children()

        # Convert the queryset to list
        children = list(children_queryset)

        self.assertIsNotNone(parent_node)

        # Save the children data before deletion
        children_before_deletion = children

        self.aNode.delete()  # Delete aNode

        # Refresh parent node from the database
        parent_node.refresh_from_db()

        # Verify that each child's parent is now the original parent of the middle node
        for child_node in children_before_deletion:
            child_node.refresh_from_db()
            self.assertEqual(child_node.parent, parent_node)

        # Verify that each child node is in the list of children of the original parent node
        parent_node.refresh_from_db()
        for child_node in children_before_deletion:
            self.assertIn(child_node, parent_node.get_children())

    def test_taxonomy_cycles(self):
        """
        Test: if the taxonomy tree has cycles
        """
        self.parent.parent = self.child2
        self.assertRaises(Exception,
                          self.parent.save)  # ToDo: Espero excepcion especifica para cuando se produce un ciclo

    def test_taxonomy_root(self):
        """
        Test: Root node
        """
        self.assertIsNone(self.parent.get_parent())

    def test_taxonomy_is_alias(self):
        """
        Test: Alias node
        """
        self.assertTrue(self.aNode_child3.is_alias)
        self.assertFalse(self.aNode_child1.is_alias)

    def test_taxonomy_is_internal(self):
        """
        Test: Alias node
        """
        self.assertTrue(self.aNode_child3.is_internal)
        self.assertFalse(self.p2_child1.is_internal)

    def test_taxonomy_internal_creation_parent_and_alias(self):
        """
        Test: Alias parent
        """
        self.assertRaises(ValidationError, Taxonomy.objects.create, type='vulnerability', name='Alias Parent',
                          alias_of=self.aNode_child1, parent=self.parent)

    def test_taxonomy_external_creation_parent_and_alias(self):
        """
        Test: Alias parent
        """
        self.assertIsInstance(Taxonomy.objects.create(type='vulnerability', name='Alias Parent',
                          alias_of=self.aNode_child1, parent=None, group=self.taxonomy_group2), Taxonomy)

    def test_taxonomy_alias_creation_parent_alias(self):
        """
        Test: Alias parent
        """
        self.assertRaises(ValidationError, Taxonomy.objects.create, type='vulnerability', name='Alias Parent',
                          alias_of=self.p2_child1_child1)

    def test_taxonomy_alias_update_alias_is_alias(self):
        """
        Test: Alias parent
        """
        with self.assertRaises(ValidationError):
            self.aNode_child1.alias_of = self.aNode_child1
            self.aNode_child1.save()

    def test_taxonomy_alias_update_parent_is_alias(self):
        """
        Test: Alias parent
        """
        with self.assertRaises(ValidationError):
            self.aNode_child4.parent = self.aNode_child3
            self.aNode_child4.save()
