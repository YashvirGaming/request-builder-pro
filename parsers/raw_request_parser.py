import re
import json

JUNK_HEADERS = {
    "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
    "sec-fetch-site", "sec-fetch-mode", "sec-fetch-dest",
    "accept-encoding", "content-length", "dnt", "priority",
    "connection",
}

KNOWN_HEADER_NAMES = {
    "host", "user-agent", "accept", "accept-language", "accept-encoding",
    "content-type", "content-length", "authorization", "origin", "referer",
    "cookie", "x-requested-with", "x-api-key", "x-auth-token", "x-csrf-token",
    "cache-control", "pragma", "connection", "dnt", "te", "upgrade-insecure-requests",
    "sec-fetch-site", "sec-fetch-mode", "sec-fetch-dest", "sec-ch-ua",
    "sec-ch-ua-mobile", "sec-ch-ua-platform", "priority",
}

HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
NOISE_MARKERS = {
    "fail keycheck", "fail key check", "success keycheck", "success key check",
    "success:", "fail:", "failure:", "keycheck:", "success check", "fail check",
    "bad response", "good response", "example response",
}


def _is_noise_line(line: str) -> bool:
    return line.strip().lower() in NOISE_MARKERS


def _is_json_start(line: str) -> bool:
    s = line.strip()
    return s.startswith("{") or s.startswith("[")


def _is_header_line(line: str) -> bool:
    """Return True only if this looks like a real HTTP header key: value."""
    s = line.strip()
    if not s or ":" not in s:
        return False
    if s.startswith("{") or s.startswith("["):
        return False
    k, _, v = s.partition(":")
    k = k.strip()
    if not k or " " in k:
        return False
    if k.lower() in KNOWN_HEADER_NAMES:
        return True
    if re.match(r'^[A-Za-z][A-Za-z0-9\-_]*$', k):
        return True
    return False


def _try_extract_json(lines: list) -> str:
    """Given a list of lines, find and return the first valid JSON object/array."""
    combined = " ".join(lines).strip()
    # Try single-line JSON first
    for line in lines:
        s = line.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                json.loads(s)
                return s
            except Exception:
                pass
    # Try multi-line reconstruction
    depth = 0
    collecting = False
    buf = []
    for line in lines:
        for ch in line:
            if ch in "{[":
                depth += 1
                collecting = True
            if collecting:
                buf.append(ch)
            if ch in "]}":
                depth -= 1
                if depth == 0 and collecting:
                    candidate = "".join(buf)
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        buf = []
                        collecting = False
                        break
    return ""


def parse_raw_request(text: str) -> dict:
    if not text or not text.strip():
        return None

    lines = text.strip().splitlines()
    method = "POST"
    url = ""
    headers = {}
    payload = ""

    idx = 0

    # ── Step 1: detect method + URL on first line ───────────────────────────
    first = lines[0].strip() if lines else ""

    # Standard HTTP format: POST /path HTTP/1.1  OR  POST https://...
    m = re.match(r'^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)', first, re.I)
    if m:
        method = m.group(1).upper()
        path   = m.group(2)
        url    = path
        idx    = 1

    # "POST: https://..." format
    elif ":" in first and first.split(":")[0].upper() in HTTP_METHODS:
        method, _, rest = first.partition(":")
        method = method.strip().upper()
        url    = rest.strip()
        idx    = 1

    # No method line — infer from content
    else:
        idx = 0

    # ── Step 2: parse headers ───────────────────────────────────────────────
    # Headers stop at: blank line, JSON body start, or noise marker
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        if not stripped:
            idx += 1
            break  # blank line = end of headers

        if _is_noise_line(stripped):
            idx += 1
            continue

        if _is_json_start(stripped):
            break  # body started without blank line

        if _is_header_line(line):
            k, _, v = stripped.partition(":")
            k = k.strip()
            v = v.strip()
            if k.lower() not in JUNK_HEADERS:
                # Merge continuation lines (indented)
                while idx + 1 < len(lines) and lines[idx + 1].startswith((" ", "\t")):
                    idx += 1
                    v += " " + lines[idx].strip()
                headers[k] = v
        # Non-header, non-JSON, non-noise line — skip (could be garbage from copy-paste)

        idx += 1

    # ── Step 3: collect body lines ──────────────────────────────────────────
    body_lines = []
    for line in lines[idx:]:
        stripped = line.strip()
        if _is_noise_line(stripped):
            break  # stop at FAIL KEYCHECK / SUCCESS: etc — they're examples, not body
        if stripped.startswith("FAIL ") or stripped.startswith("SUCCESS"):
            break
        body_lines.append(line)

    payload = _try_extract_json(body_lines)
    if not payload:
        # Fallback: raw join of body lines (form data etc)
        raw_body = "\n".join(body_lines).strip()
        if raw_body and not _is_noise_line(raw_body):
            payload = raw_body

    # ── Step 4: fix relative URL ────────────────────────────────────────────
    if url.startswith("/") and "Host" in headers:
        host = headers["Host"]
        if not host.startswith("http"):
            url = f"https://{host}{url}"

    # ── Step 5: if still no URL, try Host header ─────────────────────────────
    if not url and "Host" in headers:
        url = f"https://{headers['Host']}"

    # ── Step 6: infer method from payload ────────────────────────────────────
    if not any(m in text[:50].upper() for m in HTTP_METHODS):
        if payload:
            method = "POST"
        else:
            method = "GET"

    return {
        "method": method,
        "url":    url,
        "headers": headers,
        "payload": payload,
    }
