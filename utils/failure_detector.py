import json

FAIL_KEYWORDS = [
    "error",
    "fail",
    "invalid",
    "incorrect",
    "denied",
    "unauthorized",
    "forbidden",
    "expired",
    "not found",
    "missing",
    "required"
]

def detect_failure_keys(text):

    results = []

    try:
        data = json.loads(text)

        if isinstance(data, dict):

            for k, v in data.items():

                key = k.lower()

                if any(word in key for word in FAIL_KEYWORDS):
                    results.append(f'"{k}"')

                if isinstance(v, str):
                    val = v.lower()

                    for word in FAIL_KEYWORDS:
                        if word in val:
                            results.append(word)

    except:
        pass

    # only return 2 max
    return list(dict.fromkeys(results))[:2]