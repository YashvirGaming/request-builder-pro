import shlex


def parse_curl(curl_command):

    tokens = shlex.split(curl_command)

    method = "GET"
    url = ""
    headers = {}
    payload = ""

    i = 0

    while i < len(tokens):

        token = tokens[i]

        if token == "-X":
            method = tokens[i + 1]
            i += 1

        elif token.startswith("http"):
            url = token

        elif token == "-H":
            header = tokens[i + 1]

            if ":" in header:
                k, v = header.split(":", 1)
                headers[k.strip()] = v.strip()

            i += 1

        elif token in ["--data", "--data-raw", "--data-binary"]:
            payload = tokens[i + 1]
            method = "POST"
            i += 1

        i += 1

    return {
        "method": method,
        "url": url,
        "headers": headers,
        "payload": payload
    }