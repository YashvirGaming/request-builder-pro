import requests
import json as json_module
from utils.keyword_database import SESSION_COOKIES
from utils.token_detector import detect_tokens
from utils.jwt_detector import detect_jwt
from utils.request_detector import detect_payload_type


def send_request(req):

    session = requests.Session()

    method = req["method"]
    url = req["url"]
    headers = req["headers"]
    payload = req["payload"]

    try:
        if method == "GET":
            r = session.get(url, headers=headers, timeout=15)

        elif method == "POST":
            # FIX 3: detect payload type and send correctly as json= or data=
            payload_type = detect_payload_type(payload)

            if payload_type == "json":
                try:
                    json_data = json_module.loads(payload)
                except Exception:
                    json_data = payload
                r = session.post(url, headers=headers, json=json_data, timeout=15)
            else:
                r = session.post(url, headers=headers, data=payload, timeout=15)

        elif method == "PUT":
            payload_type = detect_payload_type(payload)
            if payload_type == "json":
                try:
                    json_data = json_module.loads(payload)
                except Exception:
                    json_data = payload
                r = session.put(url, headers=headers, json=json_data, timeout=15)
            else:
                r = session.put(url, headers=headers, data=payload, timeout=15)

        elif method == "PATCH":
            payload_type = detect_payload_type(payload)
            if payload_type == "json":
                try:
                    json_data = json_module.loads(payload)
                except Exception:
                    json_data = payload
                r = session.patch(url, headers=headers, json=json_data, timeout=15)
            else:
                r = session.patch(url, headers=headers, data=payload, timeout=15)

        elif method == "DELETE":
            r = session.delete(url, headers=headers, timeout=15)

        else:
            r = session.request(method, url, headers=headers, data=payload, timeout=15)

        text = r.text[:5000]

        detected_cookies = []
        for name, value in r.cookies.items():
            if name.lower() in SESSION_COOKIES:
                detected_cookies.append(f"{name}={value}")

        detected_tokens = detect_tokens(text)
        jwt_tokens = detect_jwt(text)

        return r.status_code, text, detected_cookies, detected_tokens, jwt_tokens

    except Exception as e:
        return "ERROR", str(e), [], [], []
