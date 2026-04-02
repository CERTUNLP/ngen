class BaseAnalyzerAdapter:
    """
    Base class for all analyzer adapters.

    Subclasses must define:
      TYPE        — string identifier (e.g. "kintun", "cortex")
      CONFIG_FIELDS — dict describing config keys:
          {"field": {"required": True/False, "sensitive": True/False}}
    """

    TYPE = None
    CONFIG_FIELDS = {}

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config

    def validate_config(self):
        """
        Validate that all required CONFIG_FIELDS are present in self.config.
        Returns a dict of field -> error message (empty if valid).
        """
        errors = {}
        for field, meta in self.CONFIG_FIELDS.items():
            if meta.get("required") and not self.config.get(field):
                errors[field] = f"'{field}' is required for {self.TYPE} analyzer."
        return errors

    def run_on_event(self, event, mapping_to):
        """
        Execute analysis on an event.
        Returns a dict with at least: vulnerable (bool), evidence (str), url (str), vuln_type (str)
        or {"error": str} on failure.
        """
        raise NotImplementedError

    def test_connection(self):
        """
        Test connectivity to the analyzer.
        Returns {"success": bool, "message": str}.
        """
        raise NotImplementedError
