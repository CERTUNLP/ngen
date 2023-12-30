from django.test import TestCase

from ngen.models import Taxonomy


class TaxonomyTestCase(TestCase):

    def setUp(self):
        """ 
        Create instances of Taxonomy
        """
        self.parent = Taxonomy.objects.create(type='vulnerability', name='Parent')
        self.child1 = Taxonomy.objects.create(type='vulnerability', name='Child 1', parent=self.parent)
        self.child2 = Taxonomy.objects.create(type='vulnerability', name='Child 2', parent=self.child1)
        self.aRootNode = Taxonomy.objects.create(type='vulnerability', name='A Root Node')
        self.aNode_Parent = Taxonomy.objects.create(type='vulnerability', name='A Node Parent')
        self.aNode = Taxonomy.objects.create(type='vulnerability', name='a Node', parent=self.aNode_Parent)
        self.aNode_child1 = Taxonomy.objects.create(type='vulnerability', name='Node Child 1', parent=self.aNode)
        self.Node_child2 = Taxonomy.objects.create(type='vulnerability', name='Node Child 2', parent=self.aNode)
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
        self.assertRaises(Exception, self.parent.save) # ToDo: Espero excepcion especifica para cuando se produce un ciclo
