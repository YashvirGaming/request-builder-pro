import json

GOOD_FIELDS = [
    "token",
    "access_token",
    "refresh_token",
    "session",
    "sessionid",
    "jwt",
    "api_key",
    "apikey",
    "csrf",
    "csrf_token",
    "id",
    "user_id"
]

def detect_response_fields(text):

    fields = []

    try:

        data = json.loads(text)

        if isinstance(data, dict):

            for key in data:

                k = key.lower()

                for good in GOOD_FIELDS:

                    if good in k:
                        fields.append(key)

    except:
        pass

    return list(set(fields))[:5]