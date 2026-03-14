import json

def parse_har(file_path):
    requests_list = []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data.get("log", {}).get("entries", []):
        req = entry.get("request", {})

        method = req.get("method")
        url = req.get("url")

        headers = {}
        for h in req.get("headers", []):
            headers[h.get("name")] = h.get("value")

        payload = ""

        if "postData" in req:
            payload = req["postData"].get("text", "")

        requests_list.append({
            "method": method,
            "url": url,
            "headers": headers,
            "payload": payload
        })

    return requests_list