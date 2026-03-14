"""
Syntax-highlighted Python code viewer widget.
tk.Text under the hood — CTkTextbox doesn't support tag colors.
Cyberpunk neon palette on pure black background.
"""
import tkinter as tk
import re

BG      = "#080810"
C_KW    = "#ff79c6"   # pink      — keywords: def class import if for try
C_DEF   = "#50fa7b"   # green     — function/method names after def
C_CLS   = "#ff79c6"   # pink bold — class names after class
C_BI    = "#8be9fd"   # cyan      — builtins: print len str dict
C_STR   = "#f1fa8c"   # yellow    — "strings" 'strings'
C_CMT   = "#44475a"   # dim grey  — # comments
C_NUM   = "#bd93f9"   # purple    — numbers
C_DEC   = "#ffb86c"   # orange    — @decorators
C_SELF  = "#ff5555"   # red       — self cls
C_CONST = "#8be9fd"   # cyan      — ALL_CAPS constants
C_PARAM = "#ffb86c"   # orange    — parameters
C_DEF_  = "#f8f8f2"   # near-white — plain text
C_OP    = "#ff5555"   # red       — operators = : ( )

KEYWORDS = {
    "import","from","as","def","class","return","yield","lambda",
    "if","elif","else","for","while","break","continue","pass",
    "try","except","finally","raise","with","assert","del","global",
    "nonlocal","in","not","and","or","is","None","True","False",
    "async","await",
}
BUILTINS = {
    "print","len","int","str","float","list","dict","set","tuple",
    "bool","type","range","enumerate","zip","map","filter","sorted",
    "open","super","hasattr","getattr","setattr","isinstance","issubclass",
    "any","all","min","max","sum","abs","round","repr","format",
    "input","id","hash","iter","next","vars","dir","callable",
    "staticmethod","classmethod","property","Exception","ValueError",
    "threading","requests","time","queue","os","re","json","datetime",
}

TOKEN_SPEC = [
    ("TDQS", r'"""[\s\S]*?"""'),
    ("TSQS", r"'''[\s\S]*?'''"),
    ("DQS",  r'"(?:\\.|[^"\\])*"'),
    ("SQS",  r"'(?:\\.|[^'\\])*'"),
    ("CMT",  r"#[^\r\n]*"),
    ("DEC",  r"@\w+"),
    ("NUM",  r"\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b"),
    ("WORD", r"\b[A-Za-z_]\w*\b"),
    ("OP",   r"[=:,()\[\]{}<>+\-*/!&|^~%]"),
    ("NL",   r"\n"),
    ("SKIP", r"[ \t\r]+"),
    ("ANY",  r"."),
]
_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC), re.DOTALL)


def _char_to_index(code: str, pos: int) -> str:
    before = code[:pos]
    row = before.count("\n") + 1
    col = pos - (before.rfind("\n") + 1)
    return f"{row}.{col}"


def _apply_highlighting(widget: tk.Text, code: str):
    widget.config(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", code)

    prev_word = None
    for m in _RE.finditer(code):
        kind  = m.lastgroup
        val   = m.group()
        start = _char_to_index(code, m.start())
        end   = _char_to_index(code, m.end())

        if kind in ("TDQS", "TSQS", "DQS", "SQS"):
            widget.tag_add("str",    start, end)
        elif kind == "CMT":
            widget.tag_add("cmt",   start, end)
        elif kind == "DEC":
            widget.tag_add("dec",   start, end)
        elif kind == "NUM":
            widget.tag_add("num",   start, end)
        elif kind == "OP":
            widget.tag_add("op",    start, end)
        elif kind == "WORD":
            if prev_word == "def":
                widget.tag_add("defname", start, end)
            elif prev_word == "class":
                widget.tag_add("clsname", start, end)
            elif val in ("self", "cls"):
                widget.tag_add("self",  start, end)
            elif val in KEYWORDS:
                widget.tag_add("kw",    start, end)
            elif val in BUILTINS:
                widget.tag_add("bi",    start, end)
            elif val.isupper() and len(val) > 1 and "_" in val or (val.isupper() and len(val) > 3):
                widget.tag_add("const", start, end)
            else:
                widget.tag_add("plain", start, end)
            prev_word = val if kind == "WORD" else None
            continue

        if kind != "WORD":
            prev_word = None

    widget.config(state="disabled")


class SyntaxCodeViewer(tk.Frame):
    """Drop-in replacement for CTkTextbox in the Generated Code tab."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, bd=0, highlightthickness=0)

        self._text = tk.Text(
            self,
            bg=BG,
            fg=C_DEF_,
            insertbackground=C_KW,
            selectbackground="#44475a",
            selectforeground="#f8f8f2",
            font=("Consolas", 11),
            wrap="none",
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            undo=True,
            state="disabled",
        )

        vsb = tk.Scrollbar(self, orient="vertical",   command=self._text.yview, bg="#111", troughcolor="#0a0a0f", bd=0, width=10)
        hsb = tk.Scrollbar(self, orient="horizontal", command=self._text.xview, bg="#111", troughcolor="#0a0a0f", bd=0, width=10)
        self._text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        self._text.pack(side="left", fill="both", expand=True)

        self._setup_tags()
        self._setup_bindings()

    def _setup_tags(self):
        t = self._text
        t.tag_configure("kw",      foreground=C_KW,    font=("Consolas", 11, "bold"))
        t.tag_configure("defname", foreground=C_DEF,   font=("Consolas", 11, "bold"))
        t.tag_configure("clsname", foreground=C_CLS,   font=("Consolas", 11, "bold"))
        t.tag_configure("bi",      foreground=C_BI)
        t.tag_configure("str",     foreground=C_STR)
        t.tag_configure("cmt",     foreground=C_CMT,   font=("Consolas", 11, "italic"))
        t.tag_configure("num",     foreground=C_NUM)
        t.tag_configure("dec",     foreground=C_DEC)
        t.tag_configure("self",    foreground=C_SELF)
        t.tag_configure("const",   foreground=C_CONST, font=("Consolas", 11, "bold"))
        t.tag_configure("op",      foreground=C_OP)
        t.tag_configure("plain",   foreground=C_DEF_)

    def _setup_bindings(self):
        t = self._text
        menu = tk.Menu(t, tearoff=0, bg="#1a1a2e", fg="#f8f8f2",
                       activebackground="#44475a", activeforeground="#f8f8f2")
        menu.add_command(label="Copy",       command=lambda: t.event_generate("<<Copy>>"))
        menu.add_command(label="Select All", command=lambda: (t.tag_add("sel","1.0","end")))
        def _show(e): menu.tk_popup(e.x_root, e.y_root)
        t.bind("<Button-3>", _show)
        t.bind("<Control-a>", lambda e: t.tag_add("sel","1.0","end"))
        t.bind("<Control-c>", lambda e: t.event_generate("<<Copy>>"))

    def set_code(self, code: str):
        _apply_highlighting(self._text, code)

    def get_code(self) -> str:
        return self._text.get("1.0", "end-1c")

    def clear(self):
        self._text.config(state="normal")
        self._text.delete("1.0", "end")
        self._text.config(state="disabled")
