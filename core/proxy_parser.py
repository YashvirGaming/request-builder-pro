def parse_proxy(proxy_line):

    proxy_line = proxy_line.strip()

    try:

        if "@" in proxy_line:
            return proxy_line

        parts = proxy_line.split(":")

        if len(parts) == 2:
            ip, port = parts
            return f"http://{ip}:{port}"

        if len(parts) == 4:
            ip, port, user, password = parts
            return f"http://{user}:{password}@{ip}:{port}"

    except:
        return None