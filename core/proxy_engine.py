from utils.request_detector import detect_payload_type


def generate_python_code(req, settings=None):

    method = req["method"]
    url = req["url"]
    headers = req["headers"]
    payload = req["payload"]

    success = ""
    failure = ""
    retry = ""

    if settings:

        success = settings.get("success", "")
        failure = settings.get("failure", "")
        retry = settings.get("retry", "")

    payload_type = detect_payload_type(payload)

    code = []

    code.append("import requests")
    code.append("import time")
    code.append("")

    code.append(f'url = "{url}"')
    code.append("")

    code.append("headers = {")

    for k, v in headers.items():
        code.append(f'    "{k}": "{v}",')

    code.append("}")
    code.append("")

    if payload:

        if payload_type == "json":
            code.append(f"json_data = {payload}")
        else:
            code.append(f"data = {repr(payload)}")

    code.append("")
    code.append("for attempt in range(3):")
    code.append("    try:")

    if method == "GET":

        code.append("        r = requests.get(url, headers=headers, timeout=15)")

    elif method == "POST":

        if payload_type == "json":

            code.append(
                "        r = requests.post(url, headers=headers, json=json_data, timeout=15)"
            )

        else:

            code.append(
                "        r = requests.post(url, headers=headers, data=data, timeout=15)"
            )

    code.append("")
    code.append("        text = r.text")

    if success:

        code.append(f'        if "{success}" in text:')
        code.append('            print("SUCCESS")')
        code.append("            break")

    if failure:

        code.append(f'        if "{failure}" in text:')
        code.append('            print("FAIL")')
        code.append("            break")

    if retry:

        code.append(f'        if "{retry}" in text:')
        code.append("            time.sleep(2)")
        code.append("            continue")

    code.append("")
    code.append("    except Exception as e:")
    code.append("        print('ERROR', e)")
    code.append("        time.sleep(2)")

    return "\n".join(code)