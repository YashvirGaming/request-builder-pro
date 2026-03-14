TOKEN_KEYWORDS = [
    "csrf",
    "xsrf",
    "token",
    "auth",
    "session"
]


def find_token_requests(requests):

    results = []

    for r in requests:

        url = (r.get("url") or "").lower()
        payload = (r.get("payload") or "").lower()

        for k in TOKEN_KEYWORDS:

            if k in url or k in payload:
                results.append(r)
                break

    return results