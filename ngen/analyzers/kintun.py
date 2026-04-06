import requests
from time import sleep
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

from ngen.analyzers.base import BaseAnalyzerAdapter


class KintunAdapter(BaseAnalyzerAdapter):
    TYPE = "kintun"
    CONFIG_FIELDS = {
        "host": {"required": True, "sensitive": False},
        "api_key": {"required": False, "sensitive": True},
        "basic_auth_username": {"required": False, "sensitive": False},
        "basic_auth_password": {"required": False, "sensitive": True},
    }

    def get_vuln_choices(self):
        try:
            r = requests.get(
                f"http://{self.config['host']}/api/vulns",
                headers=self._headers(),
                auth=self._auth(),
                timeout=10,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def _base_url(self):
        return f"http://{self.config['host']}/api"

    @staticmethod
    def _follow_redirect_post(response, headers, auth, payload):
        if response.status_code in (301, 302, 307, 308):
            location = response.headers.get("Location")
            if location:
                redirect_url = urljoin(response.url, location)
                redirected = requests.post(
                    redirect_url,
                    headers=headers,
                    auth=auth,
                    json=payload,
                    timeout=30,
                    allow_redirects=False,
                )
                redirected.raise_for_status()
                return redirected
        return response

    def _headers(self):
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.config.get("api_key"):
            headers["x-api-key"] = self.config["api_key"]
        return headers

    def _auth(self):
        username = self.config.get("basic_auth_username")
        password = self.config.get("basic_auth_password")
        if username and password:
            return HTTPBasicAuth(username, password)
        return None

    def _auth_validation_error(self):
        has_api_key = bool(self.config.get("api_key"))
        has_basic_auth = bool(self.config.get("basic_auth_username")) and bool(self.config.get("basic_auth_password"))

        if has_api_key or has_basic_auth:
            return None

        return (
            "Kintun requires authentication: provide api_key "
            "or both basic_auth_username and basic_auth_password"
        )

    def run_on_event(self, event, mapping_to):
        if not mapping_to:
            return {"error": "No vulnerability mapping found"}

        auth_error = self._auth_validation_error()
        if auth_error:
            return {"error": auth_error}

        try:
            data = {
                "vuln": mapping_to,
                "network": event.address_value,
                "ports": [],
                "params": {"feed": "test", "send-nmap-report": 0},
                "outputs": [],
                "report_to": "",
            }

            r = requests.post(
                self._base_url() + "/scan",
                headers=self._headers(),
                auth=self._auth(),
                json=data,
                timeout=30,
                allow_redirects=False,
            )
            r = self._follow_redirect_post(r, self._headers(), self._auth(), data)
            r.raise_for_status()

            scan_id = r.json()["_id"]
            scan_url = r.url.rstrip("/") + "/" + scan_id

            response = requests.get(
                scan_url, headers=self._headers(), auth=self._auth(), timeout=10
            )
            while response.json()["status"] == "started":
                sleep(1)
                response = requests.get(
                    scan_url, headers=self._headers(), auth=self._auth(), timeout=10
                )

            result = response.json().get("result")
            if result:
                vulnerable = len(result["vulnerables"]) > 0
                evidence = " ".join(
                    [
                        vuln["evidence"]
                        for vuln in (
                            result["vulnerables"] if vulnerable else result["no_vulnerables"]
                        )
                    ]
                )
            else:
                vulnerable = False
                evidence = "kintun_error"

            return {
                "vulnerable": vulnerable,
                "evidence": evidence,
                "url": scan_url,
                "vuln_type": response.json().get("vulnerability", ""),
            }
        except Exception as e:
            return {"error": str(e)}

    def test_connection(self):
        auth_error = self._auth_validation_error()
        if auth_error:
            return {"success": False, "message": auth_error}

        try:
            r = requests.get(
                self._base_url(),
                headers=self._headers(),
                auth=self._auth(),
                timeout=5,
                allow_redirects=False,
            )
            if r.status_code < 500:
                return {"success": True, "message": "Connection successful"}
            return {"success": False, "message": f"Server returned {r.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
