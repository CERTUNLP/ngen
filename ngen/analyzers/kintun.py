import logging
import requests
from time import sleep, time
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin, urlparse

from django.utils.translation import gettext_lazy as _

from ngen.analyzers.base import BaseAnalyzerAdapter

logger = logging.getLogger(__name__)


class KintunAdapter(BaseAnalyzerAdapter):
    TYPE = "kintun"
    CONFIG_FIELDS = {
        "host": {"required": True, "sensitive": False},
        "port": {"required": False, "sensitive": False, "type": "number"},
        "ssl": {"required": False, "sensitive": False, "type": "boolean"},
        "api_key": {"required": False, "sensitive": True},
        "basic_auth_username": {"required": False, "sensitive": False},
        "basic_auth_password": {"required": False, "sensitive": True},
    }

    @staticmethod
    def _follow_redirect_get(response, headers, auth):
        if response.status_code in (301, 302, 307, 308):
            location = response.headers.get("Location")
            if location:
                redirect_url = urljoin(response.url, location)
                origin_host = urlparse(response.url).netloc
                redirect_host = urlparse(redirect_url).netloc
                if redirect_host != origin_host:
                    raise ValueError(
                        f"Redirect to a different host rejected: {redirect_host!r} != {origin_host!r}"
                    )
                redirected = requests.get(
                    redirect_url,
                    headers=headers,
                    auth=auth,
                    timeout=10,
                    allow_redirects=False,
                )
                redirected.raise_for_status()
                return redirected
        return response

    def _base_url(self):
        host = self.config["host"]
        port = self.config.get("port")
        scheme = "https" if self.config.get("ssl", True) else "http"
        authority = f"{host}:{port}" if port else host
        return f"{scheme}://{authority}/api"

    def get_vuln_choices(self):
        try:
            headers = self._headers()
            auth = self._auth()
            r = requests.get(
                self._base_url() + "/vulns",
                headers=headers,
                auth=auth,
                timeout=10,
                allow_redirects=False,
            )
            r = self._follow_redirect_get(r, headers, auth)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            logger.warning("KintunAdapter.get_vuln_choices failed for host %s: %s", self.config.get("host"), exc)
            return []

    @staticmethod
    def _follow_redirect_post(response, headers, auth, payload):
        if response.status_code in (301, 302, 307, 308):
            location = response.headers.get("Location")
            if location:
                redirect_url = urljoin(response.url, location)
                origin_host = urlparse(response.url).netloc
                redirect_host = urlparse(redirect_url).netloc
                if redirect_host != origin_host:
                    raise ValueError(
                        f"Redirect to a different host rejected: {redirect_host!r} != {origin_host!r}"
                    )
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

        return _(
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

            scan_body = r.json()
            scan_id = scan_body.get("_id", "")
            if not scan_id or not str(scan_id).replace("-", "").replace("_", "").isalnum():
                return {"error": f"kintun returned invalid scan id: {scan_id!r}"}
            scan_url = r.url.rstrip("/") + "/" + str(scan_id)

            POLL_TIMEOUT = 300  # seconds
            POLL_INTERVAL_MIN = 5
            POLL_INTERVAL_MAX = 30
            deadline = time() + POLL_TIMEOUT
            poll_interval = POLL_INTERVAL_MIN

            response = requests.get(
                scan_url, headers=self._headers(), auth=self._auth(), timeout=10, allow_redirects=False
            )

            while True:
                try:
                    body = response.json()
                except ValueError:
                    return {"error": "kintun returned non-JSON response while polling"}

                scan_status = body.get("status")
                if scan_status != "started":
                    break

                if time() >= deadline:
                    return {"error": f"kintun scan timed out after {POLL_TIMEOUT}s (scan_id={scan_id})"}

                sleep(poll_interval)
                poll_interval = min(poll_interval * 2, POLL_INTERVAL_MAX)
                response = requests.get(
                    scan_url, headers=self._headers(), auth=self._auth(), timeout=10
                )

            try:
                result = body.get("result")
            except AttributeError:
                return {"error": "kintun returned unexpected response structure"}

            if result:
                vulnerables = result.get("vulnerables", [])
                no_vulnerables = result.get("no_vulnerables", [])
                vulnerable = len(vulnerables) > 0
                evidence = " ".join(
                    vuln["evidence"]
                    for vuln in (vulnerables if vulnerable else no_vulnerables)
                    if "evidence" in vuln
                )
            else:
                vulnerable = False
                evidence = "kintun_error"

            return {
                "vulnerable": vulnerable,
                "evidence": evidence,
                "url": scan_url,
                "vuln_type": body.get("vulnerability", ""),
            }
        except Exception as e:
            return {"error": str(e)}

    def test_connection(self):
        auth_error = self._auth_validation_error()
        if auth_error:
            return {"success": False, "message": auth_error}

        try:
            r = requests.get(
                self._base_url() + "/vulns",
                headers=self._headers(),
                auth=self._auth(),
                timeout=5,
                allow_redirects=False,
            )
            if r.status_code < 300:
                return {"success": True, "message": "Connection successful"}
            if r.status_code < 400:
                return {"success": False, "message": f"Unexpected redirect to {r.headers.get('Location', '?')} — check host configuration"}
            return {"success": False, "message": f"Server returned {r.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}