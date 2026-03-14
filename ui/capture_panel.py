"""
CapturePanel — multi-capture + follow-up request UI widget.
Replaces the single parse_type/val1/val2 row with:
  - N capture rows (name | method | val1 | val2 | use_as dropdown)
  - A follow-up request section (method, url, inject token as header)
"""
import tkinter as tk
import customtkinter as ctk

BG     = "#0a0a0a"
PANEL  = "#111111"
BORDER = "#1a1a2e"
NEON   = "#00fff7"
RED    = "#ff003c"
PINK   = "#ff2d78"
PURPLE = "#7b2fff"
DIM    = "#3a3a5c"
WHITE  = "#e8e8ff"

PARSE_MODES = ["json", "lr", "regex", "css", "xpath", "jsonpath"]
USE_AS_OPTIONS = [
    "capture only",
    "auth Bearer header",
    "auth Token header",
    "auth Basic header",
    "cookie",
    "query param",
    "post field",
    "x-auth-token header",
    "x-api-key header",
]


class CaptureRow(ctk.CTkFrame):
    def __init__(self, master, index, on_delete, **kw):
        super().__init__(master, fg_color="#0f0f1a", corner_radius=6, **kw)
        self.index = index

        self.name_var   = ctk.StringVar(value=f"capture{index+1}")
        self.mode_var   = ctk.StringVar(value="json")
        self.val1_var   = ctk.StringVar()
        self.val2_var   = ctk.StringVar()
        self.use_var    = ctk.StringVar(value="capture only")

        pad = dict(padx=4, pady=4)

        ctk.CTkLabel(self, text=f"#{index+1}", width=24,
            font=("Consolas",10), text_color=DIM).pack(side="left", **pad)

        ctk.CTkEntry(self, textvariable=self.name_var, width=100,
            placeholder_text="var name", fg_color=BORDER,
            text_color=NEON, font=("Consolas",11)).pack(side="left", **pad)

        ctk.CTkOptionMenu(self, variable=self.mode_var,
            values=PARSE_MODES, width=90,
            fg_color="#1a1a2e", button_color=PURPLE,
            button_hover_color=PINK, text_color=WHITE,
            font=("Consolas",11)).pack(side="left", **pad)

        ctk.CTkEntry(self, textvariable=self.val1_var, width=160,
            placeholder_text='key or left boundary',
            fg_color=BORDER, text_color=WHITE,
            font=("Consolas",11)).pack(side="left", **pad)

        ctk.CTkEntry(self, textvariable=self.val2_var, width=120,
            placeholder_text='right boundary (lr)',
            fg_color=BORDER, text_color=WHITE,
            font=("Consolas",11)).pack(side="left", **pad)

        ctk.CTkOptionMenu(self, variable=self.use_var,
            values=USE_AS_OPTIONS, width=180,
            fg_color="#1a1a2e", button_color=DIM,
            button_hover_color=PURPLE, text_color=WHITE,
            font=("Consolas",10)).pack(side="left", **pad)

        ctk.CTkButton(self, text="✕", width=28, height=26,
            fg_color="#2a0010", hover_color=RED, text_color=RED,
            font=("Consolas",12), command=on_delete).pack(side="left", **pad)

    def get_data(self) -> dict:
        return {
            "name":  self.name_var.get().strip() or f"cap{self.index+1}",
            "mode":  self.mode_var.get(),
            "val1":  self.val1_var.get().strip(),
            "val2":  self.val2_var.get().strip(),
            "use_as": self.use_var.get(),
        }


class CapturePanel(ctk.CTkFrame):
    """
    Drop-in replacement for the old parse_frame.
    Call .get_captures() -> list[dict] and .get_followup() -> dict.
    """
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=PANEL, corner_radius=8, **kw)
        self._rows: list[CaptureRow] = []

        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(8,2))

        ctk.CTkLabel(top, text="▸  CAPTURES", font=("Consolas",11,"bold"),
            text_color=PURPLE).pack(side="left")

        ctk.CTkButton(top, text="+ Add Capture", width=110, height=26,
            fg_color="#1a0a2e", hover_color=PURPLE, text_color=NEON,
            font=("Consolas",10,"bold"),
            command=self._add_row).pack(side="left", padx=8)

        ctk.CTkLabel(top,
            text="name | mode | val1 | val2 (lr only) | use captured value as",
            font=("Consolas",10), text_color=DIM).pack(side="left", padx=4)

        self._rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._rows_frame.pack(fill="x", padx=8, pady=2)

        sep = ctk.CTkFrame(self, height=1, fg_color="#1a1a2e")
        sep.pack(fill="x", padx=8, pady=4)

        self._build_followup()

    def _build_followup(self):
        fu = ctk.CTkFrame(self, fg_color="transparent")
        fu.pack(fill="x", padx=8, pady=(2,8))

        ctk.CTkLabel(fu, text="▸  FOLLOW-UP REQUEST  (optional)",
            font=("Consolas",11,"bold"), text_color=PURPLE).grid(row=0, column=0, sticky="w", padx=(0,12))

        ctk.CTkLabel(fu, text="Method", font=("Consolas",10),
            text_color=DIM).grid(row=0, column=1, padx=(0,4))

        self.fu_method = ctk.CTkOptionMenu(fu, values=["GET","POST","PUT","PATCH","DELETE"],
            width=80, fg_color="#1a1a2e", button_color=PURPLE,
            button_hover_color=PINK, text_color=WHITE,
            font=("Consolas",11))
        self.fu_method.set("GET")
        self.fu_method.grid(row=0, column=2, padx=(0,8))

        ctk.CTkLabel(fu, text="URL", font=("Consolas",10),
            text_color=DIM).grid(row=0, column=3, padx=(0,4))

        self.fu_url = ctk.CTkEntry(fu, width=320, placeholder_text="https://api.example.com/me",
            fg_color=BORDER, text_color=WHITE, font=("Consolas",11))
        self.fu_url.grid(row=0, column=4, padx=(0,8))

        ctk.CTkLabel(fu, text="Inject token as",
            font=("Consolas",10), text_color=DIM).grid(row=0, column=5, padx=(0,4))

        self.fu_inject = ctk.CTkOptionMenu(fu,
            values=["auth Bearer header", "auth Token header",
                    "x-auth-token header", "x-api-key header",
                    "cookie", "query param", "none"],
            width=180, fg_color="#1a1a2e", button_color=DIM,
            button_hover_color=PURPLE, text_color=WHITE,
            font=("Consolas",10))
        self.fu_inject.set("auth Bearer header")
        self.fu_inject.grid(row=0, column=6, padx=(0,8))

        ctk.CTkLabel(fu, text="From capture",
            font=("Consolas",10), text_color=DIM).grid(row=0, column=7, padx=(0,4))

        self.fu_from = ctk.CTkEntry(fu, width=110,
            placeholder_text="var name",
            fg_color=BORDER, text_color=NEON, font=("Consolas",11))
        self.fu_from.grid(row=0, column=8)

    def _add_row(self):
        idx = len(self._rows)
        row = CaptureRow(self._rows_frame, idx,
                         on_delete=lambda r=None, i=idx: self._delete_row(i))
        row.pack(fill="x", pady=2)
        self._rows.append(row)

    def _delete_row(self, idx):
        if idx < len(self._rows):
            self._rows[idx].destroy()
            self._rows.pop(idx)
            for i, r in enumerate(self._rows):
                r.index = i

    def get_captures(self) -> list:
        return [r.get_data() for r in self._rows if r.get_data()["val1"]]

    def get_followup(self) -> dict:
        url = self.fu_url.get().strip()
        if not url:
            return {}
        return {
            "method":  self.fu_method.get(),
            "url":     url,
            "inject":  self.fu_inject.get(),
            "from_var": self.fu_from.get().strip(),
        }
