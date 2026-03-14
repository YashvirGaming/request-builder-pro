AUTH_KEYWORDS = [
    "login",
    "signin",
    "auth",
    "token",
    "password",
    "session",
    "oauth",
    "account"
]


def filter_interesting_requests(requests):

    results = []

    seen = set()

    for r in requests:

        # 🔹 FILTER ONLY POST REQUESTS
        if r.get("method") != "POST":
            continue

        url = (r.get("url") or "").lower()

        if url in seen:
            continue

        seen.add(url)

        for k in AUTH_KEYWORDS:

            if k in url:
                results.append(r)
                break

    return results