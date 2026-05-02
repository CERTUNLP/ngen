from ngen.analyzers.kintun import KintunAdapter
from ngen.analyzers.cortex import CortexAdapter

ADAPTER_REGISTRY = {
    KintunAdapter.TYPE: KintunAdapter,
    CortexAdapter.TYPE: CortexAdapter,
}

ANALYZER_TYPE_CHOICES = [(key, key.capitalize()) for key in ADAPTER_REGISTRY]


def get_adapter(analyzer):
    """
    Return an initialized adapter instance for the given Analyzer model instance.
    Raises ValueError if the type is not registered.
    """
    adapter_class = ADAPTER_REGISTRY.get(analyzer.type)
    if not adapter_class:
        raise ValueError(f"Unknown analyzer type: '{analyzer.type}'")
    return adapter_class(analyzer)


def get_config_schema():
    """
    Return CONFIG_FIELDS for all registered types, used by the serializer
    to validate and mask sensitive fields.
    """
    return {
        adapter_class.TYPE: adapter_class.CONFIG_FIELDS
        for adapter_class in ADAPTER_REGISTRY.values()
    }


def get_vuln_choices():
    """
    Return VULN_CHOICES for all registered types.
    Empty list means the field accepts free text.
    """
    return {
        adapter_class.TYPE: getattr(adapter_class, "VULN_CHOICES", [])
        for adapter_class in ADAPTER_REGISTRY.values()
    }