import re
import json

COMMON_TOKEN_NAMES = [
    "token",
    "access_token",
    "auth",
    "authorization",
    "jwt",
    "session",
    "sessionid",
    "csrf",
    "csrf_token",
    "xsrf",
    "api_key",
    "apikey",
    "key",
    "id",
    "email"
]


def detect_tokens(text):

    found = []

    # JSON detection
    try:

        data = json.loads(text)

        if isinstance(data, dict):

            for k, v in data.items():

                if any(t in k.lower() for t in COMMON_TOKEN_NAMES):

                    found.append({
                        "name": k,
                        "value": str(v)[:60]
                    })

    except:
        pass

    # Regex fallback detection
    regex = r'"([a-zA-Z0-9_\-]*token[a-zA-Z0-9_\-]*)"\s*:\s*"([^"]+)"'

    matches = re.findall(regex, text)

    for k, v in matches:

        found.append({
            "name": k,
            "value": v[:60]
        })

    return found


def detect_token_field(payload):

    if not payload:
        return None

    payload = payload.lower()

    for name in COMMON_TOKEN_NAMES:

        if name in payload:
            return name

    return None