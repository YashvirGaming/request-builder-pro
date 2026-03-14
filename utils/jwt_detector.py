import re
import json
import base64


JWT_REGEX = r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'


def decode_part(part):

    padding = '=' * (-len(part) % 4)

    decoded = base64.urlsafe_b64decode(part + padding)

    return json.loads(decoded)


def detect_jwt(text):

    matches = re.findall(JWT_REGEX, text)

    results = []

    for token in matches:

        try:

            header, payload, sig = token.split(".")

            header_json = decode_part(header)
            payload_json = decode_part(payload)

            results.append({
                "token": token,
                "header": header_json,
                "payload": payload_json
            })

        except:
            pass

    return results