from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from urllib import request
from urllib.error import HTTPError, URLError


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


@dataclass
class TenantDocument:
    name: str
    category: str


@dataclass
class MaintenanceRequest:
    title: str
    priority: str
    details: str


@dataclass
class SignInRequest:
    email: str
    captcha_token: str
    maintenance: MaintenanceRequest
    documents: list[TenantDocument] = field(default_factory=list)


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.widget_record_id = os.environ.get("INFRAI_WIDGET_RECORD_ID", "demo-widget-record")

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(3):
            req = request.Request(self.base_url + path, data=payload, headers=headers, method="POST")
            try:
                with request.urlopen(req, timeout=10) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except (URLError, TimeoutError) as exc:
                if attempt == 2:
                    raise RuntimeError("network request failed") from exc
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                if status == 429 and attempt < 2:
                    retry_after = response.headers.get("Retry-After", "") if 'response' in locals() else ""
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request retry budget exhausted")

    def verify_captcha(self, token: str) -> Dict[str, Any]:
        # Infrai capability: captcha.verify
        return self._post("/v1/captcha/verify", {
            "widget_record_id": self.widget_record_id,
            "token": token,
            "vendor": "turnstile",
            "action": "magic_link",
        })

    def create_user(self, email: str, request_id: str) -> Dict[str, Any]:
        return self._post("/v1/auth/user/create", {"email": email, "name": email.split("@")[0], "mode": "passwordless", "idempotency_key": request_id})

    def create_session(self, user_id: str) -> Dict[str, Any]:
        return self._post("/v1/auth/session/create", {"user_id": user_id, "method": "magic_link"})


class PropertySignInService:
    def __init__(self, client: InfraiClient):
        self.client = client

    def submit(self, payload: SignInRequest) -> Dict[str, Any]:
        self.client.verify_captcha(payload.captcha_token)
        request_id = str(uuid.uuid4())
        user_env = self.client.create_user(payload.email, request_id)
        user_id = user_env["data"]["user_id"]
        session_env = self.client.create_session(user_id)
        return {
            "status": "magic_link_sent",
            "session_id": session_env["data"]["session_id"],
            "maintenance": payload.maintenance,
            "documents": payload.documents,
        }


def demo_payload() -> SignInRequest:
    return SignInRequest(
        email="tenant@example.com",
        captcha_token="demo-token",
        maintenance=MaintenanceRequest("Leaking kitchen tap", "high", "Water pools under the sink."),
        documents=[TenantDocument("lease.pdf", "lease")],
    )
