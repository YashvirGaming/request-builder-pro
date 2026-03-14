def parse_burp_request(text):

    lines = text.splitlines()

    first = lines[0].split()

    method = first[0]
    path = first[1]

    headers = {}
    body = ""

    reading_headers = True

    for line in lines[1:]:

        if reading_headers and line == "":
            reading_headers = False
            continue

        if reading_headers:

            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()

        else:
            body += line

    host = headers.get("Host", "")
    url = "https://" + host + path

    return {
        "method": method,
        "url": url,
        "headers": headers,
        "payload": body
    }