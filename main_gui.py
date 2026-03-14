import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import webbrowser

from parsers.har_parser import parse_har
from parsers.burp_parser import parse_burp_request
from parsers.http_debugger_xml_parser import parse_http_debugger_xml
from parsers.curl_parser import parse_curl
from parsers.raw_request_parser import parse_raw_request

from core.code_generator import generate_python_code
from core.formatter import format_code
from core.request_preview import preview_request
from core.request_flow import build_flow
from core.request_tester import send_request
from core.template_manager import save_template, load_template, list_templates

from utils.request_filter import filter_interesting_requests
from utils.har_analyzer import find_auth_requests
from utils.token_request_detector import find_token_requests

from ui.text_editor_utils import enable_text_editor_features
from ui.code_viewer import SyntaxCodeViewer
from ui.capture_panel import CapturePanel


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#0a0a0a"
PANEL = "#111111"
GREEN = "#00ff9c"
RED = "#ff003c"
BLUE = "#00d9ff"

class RequestBuilderGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Request Builder PRO - HTTP Automation Toolkit")
        self.root.geometry("1600x950")
        self.root.configure(fg_color=BG)

        self.requests = []
        self.selected_request = None

        top_frame = ctk.CTkFrame(root, fg_color=PANEL)
        top_frame.pack(fill="x", padx=10, pady=10)

        buttons = [
            ("Import HAR", self.load_har),
            ("Import HTTPDebugger XML", self.load_xml),
            ("Import Burp Request", self.load_burp),
            ("Import cURL", self.load_curl),
            ("Paste Raw Request", self.paste_raw_request),
            ("Save Template", self.save_template),
            ("Load Template", self.load_template),
            ("Export Script", self.export_script)
        ]

        for i, (text, cmd) in enumerate(buttons):
            ctk.CTkButton(
                top_frame, text=text, command=cmd,
                fg_color=GREEN, hover_color=BLUE, text_color="black", width=170
            ).grid(row=0, column=i, padx=6, pady=6)

        table_container = ctk.CTkFrame(self.root, fg_color=PANEL)
        table_container.pack(fill="x", padx=10, pady=5)

        header = ctk.CTkFrame(table_container, fg_color="#1f1f1f", height=32)
        header.pack(fill="x")

        ctk.CTkLabel(header, text="METHOD", width=90, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="URL", width=1050, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="DOMAIN", width=250, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)

        ctk.CTkFrame(table_container, height=2, fg_color="#333333").pack(fill="x")

        self.request_table = ctk.CTkScrollableFrame(table_container, height=180, fg_color="#0f0f0f")
        self.request_table.pack(fill="x")
        self.request_rows = []

        action_frame = ctk.CTkFrame(root, fg_color=PANEL)
        action_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(action_frame, text="Preview Request", command=self.preview, fg_color=BLUE).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Generate Python Code", command=self.generate, fg_color=GREEN, text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Send Request", command=self.test_request, fg_color=RED).pack(side="left", padx=5)

        settings_frame = ctk.CTkFrame(root, fg_color=PANEL)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="Success Keyword").grid(row=0, column=0, padx=5)
        self.success_entry = ctk.CTkEntry(settings_frame, width=200)
        self.success_entry.grid(row=0, column=1, padx=5)
        enable_text_editor_features(self.success_entry)

        ctk.CTkLabel(settings_frame, text="Failure Keyword").grid(row=0, column=2, padx=5)
        self.fail_entry = ctk.CTkEntry(settings_frame, width=200)
        self.fail_entry.grid(row=0, column=3, padx=5)
        enable_text_editor_features(self.fail_entry)

        ctk.CTkLabel(settings_frame, text="Retry Keyword").grid(row=0, column=4, padx=5)
        self.retry_entry = ctk.CTkEntry(settings_frame, width=200)
        self.retry_entry.grid(row=0, column=5, padx=5)
        enable_text_editor_features(self.retry_entry)

        self.capture_panel = CapturePanel(root)
        self.capture_panel.pack(fill="x", padx=10, pady=(4,0))

        status_bar = ctk.CTkFrame(self.root, height=40, fg_color="#0d0d0d")
        status_bar.pack(fill="x", side="bottom")

        links = [
            ("YouTube", "https://www.youtube.com/@therealyashvirgaming-shorts?sub_confirmation=1"),
            ("Telegram", "https://t.me/OFFICIALYASHVIRGAMING_GROUPCHAT"),
            ("Donate", "https://www.paypal.com/paypalme/BibiMomeenZara"),
            ("Facebook", "https://www.facebook.com/yashvirgaming.info"),
            ("Discord", "https://discord.gg/GnSCNvjBEG"),
            ("Instagram", "https://www.instagram.com/officialyashvirgaming/")
        ]

        for text, link in links:
            ctk.CTkButton(status_bar, text=text, width=90, height=26,
                fg_color="#1a1a1a", hover_color="#333333",
                command=lambda l=link: webbrowser.open(l)
            ).pack(side="left", padx=6, pady=6)

        viewer_tabs = ctk.CTkTabview(self.root)
        viewer_tabs.pack(fill="both", expand=True, padx=10, pady=10)

        viewer_tabs.add("Request")
        viewer_tabs.add("Response")
        viewer_tabs.add("Generated Code")

        self.request_view = ctk.CTkTextbox(viewer_tabs.tab("Request"), wrap="none")
        self.request_view.pack(fill="both", expand=True)

        # FIX 1: self.output did not exist — widget is self.response_view
        self.response_view = ctk.CTkTextbox(viewer_tabs.tab("Response"), wrap="none")
        self.response_view.pack(fill="both", expand=True)

        self.code_view = SyntaxCodeViewer(viewer_tabs.tab("Generated Code"))
        self.code_view.pack(fill="both", expand=True)

        enable_text_editor_features(self.request_view)
        enable_text_editor_features(self.response_view)

    def select_request(self, idx):
        self.selected_request = idx
        for i, row in enumerate(self.request_rows):
            if i == idx:
                row.configure(fg_color="#004466")
            else:
                method = self.requests[i].get("method", "GET")
                if method == "GET":
                    row.configure(fg_color="#0f2a44")
                elif method == "POST":
                    row.configure(fg_color="#0f3a2a")
                elif method == "PUT":
                    row.configure(fg_color="#3a2a0f")
                elif method == "DELETE":
                    row.configure(fg_color="#3a0f0f")
                else:
                    row.configure(fg_color="#1a1a1a")

    def load_har(self):
        file = filedialog.askopenfilename(filetypes=[("HAR files", "*.har")])
        if not file:
            return
        threading.Thread(target=self.har_worker, args=(file,), daemon=True).start()

    def har_worker(self, file):
        raw_requests = parse_har(file)
        filtered = filter_interesting_requests(raw_requests)
        if not filtered:
            filtered = raw_requests[:100]
        auth_requests = find_auth_requests(filtered)
        if auth_requests:
            self.requests = auth_requests
        else:
            self.requests = filtered
        self.flows = build_flow(self.requests)
        # FIX 4: use root.after() — never call Tkinter from a background thread
        self.root.after(0, self.update_list)

    def load_xml(self):
        file = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not file:
            return
        threading.Thread(target=self.xml_worker, args=(file,), daemon=True).start()

    def xml_worker(self, file):
        raw = parse_http_debugger_xml(file)
        filtered = filter_interesting_requests(raw)
        if not filtered:
            filtered = raw[:50]
        self.requests = filtered
        # FIX 4: use root.after() — never call Tkinter from a background thread
        self.root.after(0, self.update_list)

    def load_burp(self):
        file = filedialog.askopenfilename()
        if not file:
            return
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        req = parse_burp_request(text)
        self.requests = [req]
        self.update_list()

    def load_curl(self):
        win = tk.Toplevel(self.root)
        win.title("Paste cURL")
        txt = tk.Text(win, width=100, height=20)
        txt.pack()

        def parse():
            curl = txt.get("1.0", "end").strip()
            req = parse_curl(curl)
            self.requests = [req]
            self.update_list()
            win.destroy()

        tk.Button(win, text="Parse", command=parse).pack()

    def paste_raw_request(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Paste HTTP Request")
        win.geometry("900x500")

        txt = ctk.CTkTextbox(win, wrap="none")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        enable_text_editor_features(txt)

        def parse():
            raw = txt.get("1.0", "end").strip()
            req = None

            if raw.lower().startswith("curl "):
                try:
                    req = parse_curl(raw)
                except Exception:
                    req = None

            if req is None:
                try:
                    req = parse_raw_request(raw)
                except Exception:
                    req = None

            # FIX 2: original had "req = parse_curl(raw) / parse_raw_request(raw) / parse_burp_request(raw)"
            # which used Python's division operator between function calls — instant crash.
            # Fixed with proper fallback chain.
            if req is None:
                try:
                    req = parse_burp_request(raw)
                except Exception:
                    req = None

            if not req:
                return

            self.requests = [req]
            self.selected_request = 0
            self.update_list()
            win.destroy()

        ctk.CTkButton(win, text="Parse Request", command=parse).pack(pady=10)

    def update_list(self):
        for row in self.request_rows:
            row.destroy()
        self.request_rows = []

        for i, r in enumerate(self.requests):
            method = r.get("method", "GET")
            url = r.get("url", "")
            domain = url.split("/")[2] if "://" in url else ""

            color = "#1a1a1a"
            if method == "GET":
                color = "#0f2a44"
            elif method == "POST":
                color = "#0f3a2a"
            elif method == "PUT":
                color = "#3a2a0f"
            elif method == "DELETE":
                color = "#3a0f0f"

            row = ctk.CTkFrame(self.request_table, fg_color=color, height=30)
            row.pack(fill="x", pady=1)

            method_lbl = ctk.CTkLabel(row, text=method, width=90, anchor="w")
            method_lbl.pack(side="left", padx=5)

            url_lbl = ctk.CTkLabel(row, text=url, width=1050, anchor="w")
            url_lbl.pack(side="left", padx=5)

            domain_lbl = ctk.CTkLabel(row, text=domain, width=250, anchor="w")
            domain_lbl.pack(side="left", padx=5)

            row.bind("<Button-1>", lambda e, idx=i: self.select_request(idx))
            method_lbl.bind("<Button-1>", lambda e, idx=i: self.select_request(idx))
            url_lbl.bind("<Button-1>", lambda e, idx=i: self.select_request(idx))
            domain_lbl.bind("<Button-1>", lambda e, idx=i: self.select_request(idx))

            self.request_rows.append(row)

    def preview(self):
        if self.selected_request is None:
            return
        req = self.requests[self.selected_request]
        text = preview_request(req)
        self.request_view.delete("1.0", "end")
        self.request_view.insert("end", text)

    def test_request(self):
        if self.selected_request is None:
            return
        req = self.requests[self.selected_request]
        # FIX 3: run network call in a thread so the UI doesn't freeze
        threading.Thread(target=self._send_worker, args=(req,), daemon=True).start()

    def _send_worker(self, req):
        status, text, cookies, tokens, jwts = send_request(req)

        def update():
            # FIX 1: self.output -> self.response_view
            self.response_view.delete("1.0", "end")
            self.response_view.insert("end", f"STATUS: {status}\n\n{text}\n")

            if cookies:
                self.response_view.insert("end", "\nDetected Session Cookies:\n")
                for c in cookies:
                    self.response_view.insert("end", f"{c}\n")

            if tokens:
                self.response_view.insert("end", "\nDetected Tokens:\n")
                for t in tokens:
                    self.response_view.insert("end", f"{t['name']} -> {t['value']}\n")

            if jwts:
                import json
                self.response_view.insert("end", "\nJWT Tokens Detected:\n")
                for j in jwts:
                    self.response_view.insert("end", "\nHEADER:\n")
                    self.response_view.insert("end", json.dumps(j["header"], indent=2) + "\n")
                    self.response_view.insert("end", "\nPAYLOAD:\n")
                    self.response_view.insert("end", json.dumps(j["payload"], indent=2) + "\n")

        self.root.after(0, update)

    def save_template(self):
        win = tk.Toplevel(self.root)
        win.title("Template Name")
        entry = tk.Entry(win)
        entry.pack(pady=10)

        def save():
            name = entry.get()
            data = {
                "success": self.success_entry.get(),
                "failure": self.fail_entry.get(),
                "retry": self.retry_entry.get(),
                "parse_type": self.parse_type.get(),
                "parse_val1": self.parse_val1.get(),
                "parse_val2": self.parse_val2.get()
            }
            save_template(name, data)
            win.destroy()

        tk.Button(win, text="Save", command=save).pack()

    def load_template(self):
        win = tk.Toplevel(self.root)
        win.title("Load Template")
        lst = tk.Listbox(win)
        lst.pack()
        templates = list_templates()
        for t in templates:
            lst.insert(tk.END, t)

        def load():
            idx = lst.curselection()
            if not idx:
                return
            name = lst.get(idx)
            data = load_template(name)
            self.success_entry.delete(0, tk.END)
            self.success_entry.insert(0, data.get("success", ""))
            self.fail_entry.delete(0, tk.END)
            self.fail_entry.insert(0, data.get("failure", ""))
            self.retry_entry.delete(0, tk.END)
            self.retry_entry.insert(0, data.get("retry", ""))
            self.parse_type.set(data.get("parse_type", "none"))
            self.parse_val1.delete(0, tk.END)
            self.parse_val1.insert(0, data.get("parse_val1", ""))
            self.parse_val2.delete(0, tk.END)
            self.parse_val2.insert(0, data.get("parse_val2", ""))
            win.destroy()

        tk.Button(win, text="Load", command=load).pack()

    def export_script(self):
        code = self.code_view.get_code().strip()
        if not code:
            return
        path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

    def generate(self):
        if self.selected_request is None:
            return
        req = self.requests[self.selected_request]

        settings = {
            "success_response": self.success_entry.get(),
            "fail_response":    self.fail_entry.get(),
            "retry":            self.retry_entry.get(),
            "captures":         self.capture_panel.get_captures(),
            "followup":         self.capture_panel.get_followup(),
        }

        code = generate_python_code(req, settings)
        code = format_code(code)
        self.code_view.set_code(code)


root = ctk.CTk()
app = RequestBuilderGUI(root)
root.mainloop()
