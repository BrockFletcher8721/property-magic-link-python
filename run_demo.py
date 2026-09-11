import json

from src.magic_link_service import PropertySignInService, InfraiClient, demo_payload


if __name__ == "__main__":
    result = PropertySignInService(InfraiClient()).submit(demo_payload())
    print(json.dumps({"status": result["status"], "session_id": result["session_id"]}))

