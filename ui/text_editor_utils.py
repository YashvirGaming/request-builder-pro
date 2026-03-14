import tkinter as tk


def enable_text_editor_features(widget):

    try:
        widget.configure(undo=True)
    except Exception:
        pass

    menu = tk.Menu(widget, tearoff=0)

    menu.add_command(label="Undo", command=lambda: widget.event_generate("<<Undo>>"))
    menu.add_command(label="Redo", command=lambda: widget.event_generate("<<Redo>>"))
    menu.add_separator()
    menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_separator()

    # FIX 6: tag_add only exists on Text/CTkTextbox — Entry uses select_range(0, "end")
    # Detect which type of widget we have and call the correct method
    def select_all():
        try:
            # Text widget (CTkTextbox wraps this)
            widget.tag_add("sel", "1.0", "end")
        except AttributeError:
            try:
                # Entry widget
                widget.select_range(0, "end")
                widget.icursor("end")
            except Exception:
                pass

    menu.add_command(label="Select All", command=select_all)

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    widget.bind("<Button-3>", show_menu)

    def _select_all(e):
        select_all()
        return "break"

    widget.bind("<Control-a>", _select_all)
    widget.bind("<Control-z>", lambda e: widget.event_generate("<<Undo>>"))
    widget.bind("<Control-y>", lambda e: widget.event_generate("<<Redo>>"))
    widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))
    widget.bind("<Control-x>", lambda e: widget.event_generate("<<Cut>>"))
