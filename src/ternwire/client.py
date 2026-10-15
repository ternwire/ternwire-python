from __future__ import annotations

import ipaddress
import json
import math
import re
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

DEFAULT_BASE_URL = "https://ternwire.com"


class TernwireApiError(Exception):
    def __init__(self, status: int, raw_body: str, headers: dict[str, str]):
        super().__init__(f"Ternwire API returned HTTP {status}")
        self.status = status
        self.raw_body = raw_body
        self.headers = headers
        try:
            self.body: Any = json.loads(raw_body)
        except ValueError:
            self.body = None


def _is_loopback_host(host: str) -> bool:
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class TernwireClient:
    def __init__(self, api_key: str, base_url: str | None = None, timeout: float = 30):
        if not re.fullmatch(r"em_(live|test)_[A-Za-z0-9_-]+", api_key):
            raise ValueError("Use an em_live_ or em_test_ API key")
        if base_url is None:
            base_url = DEFAULT_BASE_URL
        origin = urlsplit(base_url)
        if (origin.scheme not in ("http", "https") or not origin.hostname
                or origin.username or origin.password or origin.path not in ("", "/")
                or origin.query or origin.fragment):
            raise ValueError("base_url must be an HTTP(S) origin without /v1")
        loopback = _is_loopback_host(origin.hostname)
        if origin.scheme == "http" and not loopback:
            raise ValueError(
                "base_url must use https unless it points at localhost or a loopback address")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be positive and finite")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        # A proxy cannot reach this machine's loopback, and would receive the API key.
        handlers = [ProxyHandler({})] if loopback else []
        self._opener = build_opener(*handlers, _NoRedirect())

    @staticmethod
    def _id(value: str) -> str:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{7,127}", value):
            raise ValueError("Invalid Ternwire resource ID")
        return value

    @staticmethod
    def _query(values: dict[str, Any]) -> str:
        present = {name: value for name, value in values.items() if value is not None}
        return "?" + urlencode(present) if present else ""

    # BEGIN GENERATED OPERATIONS
    def submit_email(self, input: dict[str, Any], idempotency_key: str) -> dict[str, Any] | None:
        if not isinstance(input, dict):
            raise ValueError("input must be a dictionary")
        if not isinstance(idempotency_key, str):
            raise ValueError("idempotency_key is required")
        return self._request("POST", "/v1/emails", 202, input, idempotency_key)

    def get_message(self, message_id: str) -> dict[str, Any] | None:
        return self._request("GET", "/v1/emails/" + self._id(message_id), 200, None, None)

    def create_email_template(self, input: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(input, dict):
            raise ValueError("input must be a dictionary")
        return self._request("POST", "/v1/templates", 201, input, None)

    def list_email_templates(self, *, cursor: str | None = None, limit: int | None = None) -> dict[str, Any] | None:
        return self._request("GET", "/v1/templates" + self._query({"cursor": cursor, "limit": limit}), 200, None, None)

    def get_email_template(self, template_id: str) -> dict[str, Any] | None:
        return self._request("GET", "/v1/templates/" + self._id(template_id), 200, None, None)

    def replace_email_template(self, template_id: str, input: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(input, dict):
            raise ValueError("input must be a dictionary")
        return self._request("PUT", "/v1/templates/" + self._id(template_id), 200, input, None)

    def delete_email_template(self, template_id: str) -> dict[str, Any] | None:
        return self._request("DELETE", "/v1/templates/" + self._id(template_id), 204, None, None)

    def create_attachment_upload_slot(self, input: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(input, dict):
            raise ValueError("input must be a dictionary")
        return self._request("POST", "/v1/attachments", 201, input, None)

    def get_attachment(self, attachment_id: str) -> dict[str, Any] | None:
        return self._request("GET", "/v1/attachments/" + self._id(attachment_id), 200, None, None)

    def complete_attachment_upload(self, attachment_id: str) -> dict[str, Any] | None:
        return self._request("POST", "/v1/attachments/" + self._id(attachment_id) + "/complete", 202, None, None)

    def create_sending_domain(self, input: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(input, dict):
            raise ValueError("input must be a dictionary")
        return self._request("POST", "/v1/domains", 201, input, None)

    def get_sending_domain(self, domain_id: str) -> dict[str, Any] | None:
        return self._request("GET", "/v1/domains/" + self._id(domain_id), 200, None, None)

    def delete_sending_domain(self, domain_id: str) -> dict[str, Any] | None:
        return self._request("DELETE", "/v1/domains/" + self._id(domain_id), 202, None, None)

    def create_webhook_endpoint(self, input: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(input, dict):
            raise ValueError("input must be a dictionary")
        return self._request("POST", "/v1/webhook-endpoints", 201, input, None)

    def rotate_webhook_endpoint_signing_secret(self, endpoint_id: str) -> dict[str, Any] | None:
        return self._request("POST", "/v1/webhook-endpoints/" + self._id(endpoint_id) + "/rotate-signing-secret", 200, None, None)

    def get_webhook_attempt(self, attempt_id: str) -> dict[str, Any] | None:
        return self._request("GET", "/v1/webhook-attempts/" + self._id(attempt_id), 200, None, None)

    def replay_webhook_attempt(self, attempt_id: str) -> dict[str, Any] | None:
        return self._request("POST", "/v1/webhook-attempts/" + self._id(attempt_id) + "/replay", 202, None, None)
    # END GENERATED OPERATIONS

    def _request(self, method: str, path: str, expected_status: int,
                 body: dict[str, Any] | None = None,
                 idempotency_key: str | None = None) -> dict[str, Any] | None:
        headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
        if idempotency_key is not None:
            if not re.fullmatch(r"[\x21-\x7e]{1,128}", idempotency_key):
                raise ValueError("idempotency_key must contain 1-128 visible ASCII characters")
            headers["Idempotency-Key"] = idempotency_key
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body, allow_nan=False).encode("utf-8")
        request = Request(self._base_url + path, data=data, headers=headers, method=method)
        try:
            response = self._opener.open(request, timeout=self._timeout)
        except HTTPError as error:
            with error:
                raise TernwireApiError(error.code, error.read().decode("utf-8", errors="replace"),
                                      dict(error.headers.items())) from None
        with response:
            raw_body = response.read().decode("utf-8")
            if response.status != expected_status:
                raise TernwireApiError(response.status, raw_body, dict(response.headers.items()))
            if expected_status == 204:
                return None
            payload = json.loads(raw_body)
            if not isinstance(payload, dict):
                raise ValueError("Ternwire API returned a non-object JSON response")
            return payload
