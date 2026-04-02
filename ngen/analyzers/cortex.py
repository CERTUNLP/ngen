from ngen.analyzers.base import BaseAnalyzerAdapter


class CortexAdapter(BaseAnalyzerAdapter):
    TYPE = "cortex"
    CONFIG_FIELDS = {
        "host": {"required": True, "sensitive": False},
        "api_key": {"required": True, "sensitive": True},
        "organization": {"required": False, "sensitive": False},
    }

    def _get_api(self):
        from cortex4py.api import Api
        from cortex4py.exceptions import CortexException

        host = f"http://{self.config['host']}"
        try:
            api = Api(host, self.config["api_key"])
            api.status()
            return api
        except CortexException:
            return None

    def run_on_event(self, event, mapping_to):
        return {"error": "Cortex does not support event scanning directly"}

    def test_connection(self):
        api = self._get_api()
        if api:
            return {"success": True, "message": "Connection successful"}
        return {"success": False, "message": "Could not connect to Cortex"}
