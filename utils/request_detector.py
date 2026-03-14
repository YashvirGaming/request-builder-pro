import json
import urllib.parse


def detect_payload_type(payload):

    if not payload:
        return "raw"

    payload = payload.strip()

    # GraphQL — JSON with a "query" key containing GQL syntax
    if payload.startswith("{") or payload.startswith("["):
        try:
            d = json.loads(payload)
            if isinstance(d, dict) and "query" in d and isinstance(d.get("query"), str):
                return "graphql"
            return "json"
        except Exception:
            pass

    # URL-encoded form
    if "=" in payload:
        try:
            parsed = urllib.parse.parse_qs(payload, keep_blank_values=True)
            if parsed:
                return "form"
        except Exception:
            pass

    return "raw"
