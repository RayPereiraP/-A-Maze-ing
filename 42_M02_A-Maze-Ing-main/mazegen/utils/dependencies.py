# ----- IMPORTS -----

try:
    from pydantic import (BaseModel, Field, ValidationError,
                          model_validator, PrivateAttr)
    from rich import print
    from rich.text import Text
    from rich.panel import Panel


except ModuleNotFoundError:
    print("ERROR: Missing required dependencies!")
    print("\nInstall dependencies with:\n    - make install")
    # print("\nInstall dependencies:\n")
    # print("- using pip:")
    # print("   pip install -r requirements.txt")
    # print("\n- using Poetry:")
    # print("   poetry install")
    # print("   poetry run python loading.py")
    print("\nThen run the program again. :)")
    exit(1)  # make exits with error


# ----- FORMATTING -----

BOLD = "[bold]"
ITALIC = "[italic]"
RESET = "[/]"

RED = "[red]"
GREEN = "[green]"
YELLOW = "[yellow]"
BLUE = "[blue]"

# combinations
BOLD_RED = "[bold red]"
BOLD_GREEN = "[bold green]"
BOLD_BLUE = "[bold blue]"


__all__ = [
    # library imports
    "BaseModel", "Field", "ValidationError", "model_validator", "PrivateAttr",

    # rich print and formatting
    "print", "Text", "Panel",
    "BOLD", "ITALIC", "RESET",
    "RED", "GREEN", "YELLOW", "BLUE",
    "BOLD_RED", "BOLD_GREEN", "BOLD_BLUE",
]
