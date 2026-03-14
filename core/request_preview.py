import json


def preview_request(req):

    preview = []

    preview.append(f"METHOD: {req['method']}")
    preview.append(f"URL: {req['url']}")
    preview.append("")

    preview.append("HEADERS:")

    for k, v in req["headers"].items():
        preview.append(f"{k}: {v}")

    preview.append("")
    preview.append("PAYLOAD:")

    payload = req["payload"]

    if payload:

        try:
            payload = json.dumps(json.loads(payload), indent=4)
        except:
            pass

    preview.append(str(payload))

    return "\n".join(preview)