LOGIN_KEYWORDS = [
    "login",
    "signin",
    "auth",
    "token",
    "password",
    "session",
    "oauth"
]


def detect_login_requests(requests):

    detected = []

    for r in requests:

        url = (r.get("url") or "").lower()
        payload = (r.get("payload") or "").lower()

        for k in LOGIN_KEYWORDS:

            if k in url or k in payload:
                detected.append(r)
                break

    return detected