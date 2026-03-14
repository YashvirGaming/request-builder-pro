LOGIN_KEYWORDS = [
    "login",
    "signin",
    "auth",
    "token",
    "password",
    "session"
]


def find_auth_requests(requests):

    results = []

    for r in requests:

        url = (r.get("url") or "").lower()
        payload = (r.get("payload") or "").lower()

        for k in LOGIN_KEYWORDS:

            if k in url or k in payload:
                results.append(r)
                break

    return results