def _background(style: str, text: str) -> str:
    """Wrap a text block in Rich background color style."""
    return f"[on {style}]{text}[/]"


THEMES = {

    "default": {
        "WALL":    _background("black", "  "),
        "EMPTY":   _background("cyan", "  "),
        "ENTRY":   _background("bright_magenta", "  "),
        "EXIT":    _background("bright_magenta", "  "),
        "PATH":    _background("#ffffff", "  "),
        "PATTERN": _background("yellow", "  "),
    },

    "neon": {
        "WALL":    _background("black", "  "),
        "EMPTY":   _background("bright_white", "  "),
        "ENTRY":   _background("bright_green", "  "),
        "EXIT":    _background("bright_red", "  "),
        "PATH":    _background("bright_blue", "  "),
        "PATTERN": _background("black", "  "),
    },

    "pastel": {
        "WALL":    _background("grey70", "  "),
        "EMPTY":   _background("grey35", "  "),
        "ENTRY":   _background("green3", "  "),
        "EXIT":    _background("red3", "  "),
        "PATH":    _background("cornflower_blue", "  "),
        "PATTERN": _background("dark_goldenrod", "  "),
    },

    "mono": {
        "WALL":    _background("bright_white", "  "),
        "EMPTY":   _background("black", "  "),
        "ENTRY":   _background("grey30", "  "),
        "EXIT":    _background("grey30", "  "),
        "PATH":    _background("grey70", "  "),
        "PATTERN": _background("grey50", "  "),
    },
}
