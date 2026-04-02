"""
Django Unit Tests for Analyzer and AnalyzerMapping models
"""

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from ngen.models import Analyzer, Taxonomy
from ngen.models.analyzer_mapping import AnalyzerMapping


class AnalyzerTest(TestCase):
    """
    Tests for the Analyzer model: creation, validation, and adapter wiring.
    """

    fixtures = ["tests/taxonomy.json"]

    @classmethod
    def setUpTestData(cls):
        cls.valid_config = {"host": "kintun.example.com"}
        cls.analyzer = Analyzer.objects.create(
            name="Kintun Test",
            type="kintun",
            config=cls.valid_config,
        )

    # --- creation ---

    def test_analyzer_creation(self):
        self.assertIsInstance(self.analyzer, Analyzer)

    def test_default_enabled(self):
        self.assertTrue(self.analyzer.enabled)

    def test_str(self):
        self.assertEqual(str(self.analyzer), "Kintun Test")

    # --- type validation ---

    def test_invalid_type_raises_validation_error(self):
        analyzer = Analyzer(name="Bad", type="nonexistent", config={})
        with self.assertRaises(ValidationError) as ctx:
            analyzer.full_clean()
        self.assertIn("type", ctx.exception.message_dict)

    def test_valid_type_passes_validation(self):
        analyzer = Analyzer(name="Valid", type="kintun", config=self.valid_config)
        try:
            analyzer.full_clean()
        except ValidationError as e:
            self.fail(f"full_clean() raised ValidationError unexpectedly: {e}")

    # --- config validation ---

    def test_missing_required_config_raises_validation_error(self):
        analyzer = Analyzer(name="No host", type="kintun", config={})
        with self.assertRaises(ValidationError) as ctx:
            analyzer.full_clean()
        self.assertIn("config", ctx.exception.message_dict)

    def test_valid_config_passes_clean(self):
        analyzer = Analyzer(
            name="Full config",
            type="kintun",
            config={"host": "kintun.example.com", "api_key": "secret"},
        )
        try:
            analyzer.full_clean()
        except ValidationError as e:
            self.fail(f"full_clean() raised ValidationError unexpectedly: {e}")

    # --- adapter ---

    def test_get_adapter_returns_correct_type(self):
        from ngen.analyzers.kintun import KintunAdapter

        adapter = self.analyzer.get_adapter()
        self.assertIsInstance(adapter, KintunAdapter)

    def test_get_adapter_unknown_type_raises_value_error(self):
        analyzer = Analyzer(name="X", type="unknown", config={})
        with self.assertRaises(ValueError):
            analyzer.get_adapter()


class AnalyzerMappingTest(TestCase):
    """
    Tests for the AnalyzerMapping model: creation, constraints, and cascades.
    """

    fixtures = ["tests/taxonomy.json"]

    @classmethod
    def setUpTestData(cls):
        cls.taxonomy = Taxonomy.objects.get(slug="blacklist")
        cls.analyzer = Analyzer.objects.create(
            name="Kintun Mapping Test",
            type="kintun",
            config={"host": "kintun.example.com"},
        )

    def _make_mapping(self, mapping_to="amqp"):
        return AnalyzerMapping.objects.create(
            mapping_from=self.taxonomy,
            mapping_to=mapping_to,
            analyzer=self.analyzer,
        )

    # --- creation ---

    def test_mapping_creation(self):
        mapping = self._make_mapping()
        self.assertIsInstance(mapping, AnalyzerMapping)

    def test_mapping_to_value(self):
        mapping = self._make_mapping("snmp")
        self.assertEqual(mapping.mapping_to, "snmp")

    def test_mapping_from_relation(self):
        mapping = self._make_mapping()
        self.assertEqual(mapping.mapping_from, self.taxonomy)

    def test_mapping_analyzer_relation(self):
        mapping = self._make_mapping()
        self.assertEqual(mapping.analyzer, self.analyzer)

    def test_str(self):
        mapping = self._make_mapping()
        expected = f"Mapping {mapping.id} for Taxonomy {self.taxonomy.id} ({self.analyzer.name})"
        self.assertEqual(str(mapping), expected)

    # --- PROTECT constraint ---

    def test_delete_analyzer_with_mappings_raises_protected_error(self):
        analyzer = Analyzer.objects.create(
            name="Deletable Analyzer",
            type="kintun",
            config={"host": "kintun.example.com"},
        )
        AnalyzerMapping.objects.create(
            mapping_from=self.taxonomy,
            mapping_to="rdp",
            analyzer=analyzer,
        )
        with self.assertRaises(ProtectedError):
            analyzer.delete()

    def test_delete_analyzer_without_mappings_succeeds(self):
        analyzer = Analyzer.objects.create(
            name="Safe to delete",
            type="kintun",
            config={"host": "kintun.example.com"},
        )
        try:
            analyzer.delete()
        except ProtectedError:
            self.fail("delete() raised ProtectedError on an analyzer with no mappings")

    # --- CASCADE from taxonomy ---

    def test_delete_taxonomy_cascades_to_mappings(self):
        taxonomy = Taxonomy.objects.create(
            type="vulnerability", name="Temp Taxonomy", slug="temp-taxonomy"
        )
        mapping = AnalyzerMapping.objects.create(
            mapping_from=taxonomy,
            mapping_to="telnet",
            analyzer=self.analyzer,
        )
        mapping_id = mapping.id
        taxonomy.delete()
        self.assertFalse(AnalyzerMapping.objects.filter(pk=mapping_id).exists())

    # --- reverse relation ---

    def test_analyzer_mappings_reverse_relation(self):
        analyzer = Analyzer.objects.create(
            name="Multi-mapping Analyzer",
            type="kintun",
            config={"host": "kintun.example.com"},
        )
        AnalyzerMapping.objects.create(
            mapping_from=self.taxonomy, mapping_to="amqp", analyzer=analyzer
        )
        AnalyzerMapping.objects.create(
            mapping_from=self.taxonomy, mapping_to="snmp", analyzer=analyzer
        )
        self.assertEqual(analyzer.mappings.count(), 2)
