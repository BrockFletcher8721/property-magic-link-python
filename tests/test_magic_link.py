import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.magic_link_service import MaintenanceRequest, PropertySignInService, SignInRequest


class FakeClient:
    def __init__(self):
        self.calls = []

    def verify_captcha(self, token):
        self.calls.append(("captcha", token))
        return {"ok": True, "data": {}}

    def create_user(self, email, request_id):
        self.calls.append(("user", email, request_id))
        return {"ok": True, "data": {"user_id": "user-42"}}

    def create_session(self, user_id):
        self.calls.append(("session", user_id))
        return {"ok": True, "data": {"session_id": "session-42"}}


def test_sign_in_keeps_maintenance_context():
    service = PropertySignInService(FakeClient())
    result = service.submit(SignInRequest("a@tenant.test", "captcha", MaintenanceRequest("Broken lock", "urgent", "Front door sticks.")))
    assert result["status"] == "magic_link_sent"
    assert result["session_id"] == "session-42"
    assert result["maintenance"].title == "Broken lock"
