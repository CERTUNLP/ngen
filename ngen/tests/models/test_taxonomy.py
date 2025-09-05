from django.core.exceptions import ValidationError  # type: ignore
from django.test import TestCase  # type: ignore

from ngen.models import Taxonomy, TaxonomyGroup
from ngen.models.taxonomy import Report


class TaxonomyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create instances of Taxonomy for testing.
        """
        cls.parent = Taxonomy.objects.create(type="vulnerability", name="Parent")
        cls.child1 = Taxonomy.objects.create(
            type="vulnerability", name="Child 1", parent=cls.parent
        )
        cls.child2 = Taxonomy.objects.create(
            type="vulnerability", name="Child 2", parent=cls.child1
        )
        cls.aRootNode = Taxonomy.objects.create(
            type="vulnerability", name="A Root Node"
        )
        cls.aNode_Parent = Taxonomy.objects.create(
            type="vulnerability", name="A Node Parent"
        )
        cls.aNode = Taxonomy.objects.create(
            type="vulnerability", name="a Node", parent=cls.aNode_Parent
        )
        cls.aNode_child1 = Taxonomy.objects.create(
            type="vulnerability", name="Node Child 1", parent=cls.aNode
        )
        cls.aNode_child2 = Taxonomy.objects.create(
            type="vulnerability", name="Node Child 2", parent=cls.aNode
        )
        cls.aNode_child3 = Taxonomy.objects.create(
            type="vulnerability", name="Node Child 3", alias_of=cls.aNode
        )
        cls.aNode_child4 = Taxonomy.objects.create(
            type="vulnerability", name="Node Child 4", alias_of=cls.child1
        )

        cls.taxonomy_group2 = TaxonomyGroup.objects.create(name="Shadowserver")
        cls.parent2 = Taxonomy.objects.create(
            type="incident", name="Parent2", group=cls.taxonomy_group2
        )
        cls.p2_child1 = Taxonomy.objects.create(
            type="incident", name="P2 Child 1", parent=cls.parent2
        )
        cls.p2_child2 = Taxonomy.objects.create(
            type="incident", name="P2 Child 2", parent=cls.parent2
        )
        cls.p2_child1_child1 = Taxonomy.objects.create(
            type="incident",
            name="P2 Child 1 Child 1",
            parent=cls.p2_child1,
            alias_of=cls.aNode_child2,
        )
        cls.setUpReports()
    @classmethod 
    def setUpReports(cls):
        """
        Create example Taxonomy and Reports for testing.
        """
        cls.taxonomy = Taxonomy.objects.create(
            name="Test Taxonomy", type="incident"
        )
        Report.objects.create(
            taxonomy=cls.taxonomy, lang="en", problem="Test problem"
        )
        Report.objects.create(
            taxonomy=cls.taxonomy, lang="es", problem="Problema de prueba"
        )

    def test_get_matching_report_in_english(self):
        """
        Test: Retrieve matching report in English.
        """
        report = self.taxonomy.get_matching_report(lang="en")
        self.assertEqual(report[0].problem, "Test problem")

    def test_get_matching_report_in_spanish(self):
        """
        Test: Retrieve matching report in Spanish.
        """
        report = self.taxonomy.get_matching_report(lang="es")
        self.assertEqual(report[0].problem, "Problema de prueba")

    def test_get_matching_report_not_found(self):
        """
        Test: No matching report for the requested language.
        """
        report = self.taxonomy.get_matching_report(lang="fr")
        self.assertEqual(len(report), 0)

    def test_node_deletion(self):
        """
        Test: Simple deletion of a node.
        """
        self.aNode.delete()
        deleted_node = Taxonomy.objects.filter(id=self.aNode.id).first()
        self.assertIsNone(deleted_node)

    def test_parent_deletion(self):
        """
        Test: If a root parent is deleted, all children must NOT have a parent.
        """
        children = list(self.aRootNode.get_children())
        self.aRootNode.delete()

        for child in children:
            child.refresh_from_db()
            self.assertIsNone(child.parent)

    def test_middle_node_deletion(self):
        """
        Test: If a middle node is deleted, parent and children should be connected.
        """
        parent_node = self.aNode.get_parent()
        children = list(self.aNode.get_children())

        self.assertIsNotNone(parent_node)

        self.aNode.delete()

        parent_node.refresh_from_db()
        for child_node in children:
            child_node.refresh_from_db()
            self.assertEqual(child_node.parent, parent_node)

    def test_taxonomy_cycles(self):
        """
        Test: Ensure the taxonomy tree does not allow cycles.
        """
        self.parent.parent = self.child2
        with self.assertRaises(ValidationError):
            self.parent.save()

    def test_taxonomy_root(self):
        """
        Test: Verify root node has no parent.
        """
        self.assertIsNone(self.parent.get_parent())

    def test_taxonomy_is_alias(self):
        """
        Test: Verify alias nodes.
        """
        self.assertTrue(self.aNode_child3.is_alias)
        self.assertFalse(self.aNode_child1.is_alias)

    def test_taxonomy_is_internal(self):
        """
        Test: Verify internal nodes.
        """
        self.assertTrue(self.aNode_child3.is_internal)
        self.assertFalse(self.p2_child1.is_internal)

    def test_taxonomy_internal_creation_parent_and_alias(self):
        """
        Test: Alias parent creation validation.
        """
        with self.assertRaises(ValidationError):
            Taxonomy.objects.create(
                type="vulnerability",
                name="Alias Parent",
                alias_of=self.aNode_child1,
                parent=self.parent,
            )

    def test_taxonomy_external_creation_parent_and_alias(self):
        """
        Test: External alias creation with a group.
        """
        taxonomy = Taxonomy.objects.create(
            type="vulnerability",
            name="Alias Parent",
            alias_of=self.aNode_child1,
            parent=None,
            group=self.taxonomy_group2,
        )
        self.assertIsInstance(taxonomy, Taxonomy)

    def test_taxonomy_alias_creation_parent_alias(self):
        """
        Test: Alias creation validation.
        """
        with self.assertRaises(ValidationError):
            Taxonomy.objects.create(
                type="vulnerability",
                name="Alias Parent",
                alias_of=self.p2_child1_child1,
            )

    def test_taxonomy_alias_update_alias_is_alias(self):
        """
        Test: Alias update validation.
        """
        with self.assertRaises(ValidationError):
            self.aNode_child1.alias_of = self.aNode_child1
            self.aNode_child1.save()

    def test_taxonomy_alias_update_parent_is_alias(self):
        """
        Test: Parent alias update validation.
        """
        with self.assertRaises(ValidationError):
            self.aNode_child4.parent = self.aNode_child3
            self.aNode_child4.save()

    def test_create_taxonomy(self):
        """
        Test: Verify taxonomy creation.
        """
        self.assertEqual(self.parent.name, "Parent")
        self.assertEqual(self.child1.parent, self.parent)

    def test_is_internal_property(self):
        """
        Test: Verify is_internal property.
        """
        self.assertEqual(self.child1.is_internal, self.child1.group is None)
        self.assertEqual(self.aNode_child3.is_internal, self.child1.group is None)
        self.assertEqual(not self.parent2.is_internal, self.parent2.group is not None)

    def test_is_alias_property(self):
        """
        Test: Verify is_alias property.
        """
        self.assertTrue(self.aNode_child3.is_alias)

    def test_alias_of_itself_raises_error(self):
        """
        Test: Taxonomy cannot be an alias of itself.
        """
        with self.assertRaises(ValidationError):
            alias = Taxonomy(name="Invalid Alias", alias_of=self.parent)
            alias.full_clean()

    def test_alias_of_alias_raises_error(self):
        """
        Test: Taxonomy cannot be an alias of another alias.
        """
        with self.assertRaises(ValidationError):
            alias = Taxonomy(name="Alias", alias_of=self.aNode_child3)
            alias.full_clean()

        
   