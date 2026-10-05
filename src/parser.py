"""Read and validate the maze configuration described in the subject."""

from pathlib import Path
from typing import Dict, Tuple, Union, cast


ConfigValue = Union[int, bool, str, Tuple[int, int]]
Config = Dict[str, ConfigValue]
REQUIRED_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


class ConfigError(ValueError):
    """Report an unreadable or invalid configuration file."""


def parse_value(key: str, value: str) -> ConfigValue:
    """Convert known settings; preserve additional settings as strings."""
    if key in ("WIDTH", "HEIGHT", "SEED"):
        try:
            number = int(value)
        except ValueError:
            raise ConfigError(f"{key} must be an integer.") from None
        if key in ("WIDTH", "HEIGHT") and number <= 0:
            raise ConfigError(f"{key} must be greater than zero.")
        return number
    if key in ("ENTRY", "EXIT"):
        parts = value.split(",")
        if len(parts) != 2:
            raise ConfigError(f"{key} must have the format x,y.")
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            raise ConfigError(f"{key} must contain two integers.") from None
    if key == "PERFECT":
        if value.lower() not in ("true", "false"):
            raise ConfigError("PERFECT must be True or False.")
        return value.lower() == "true"
    return value


def parse_config(filename: Union[str, Path]) -> Config:
    """Read KEY=VALUE lines and return a dictionary of validated settings.

    Ignore blank lines and full-line comments. Reject duplicate keys, empty
    values and malformed lines. Optional unknown keys retain string values.
    Raise ConfigError on file errors or invalid maze parameters.
    """
    config: Config = {}
    try:
        with open(filename, encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, separator, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if not separator or not key or not value:
                    raise ConfigError(
                        f"Line {line_number}: expected KEY=VALUE."
                    )
                if key in config:
                    raise ConfigError(
                        f"Line {line_number}: duplicate key {key}."
                    )
                try:
                    config[key] = parse_value(key, value)
                except ConfigError as error:
                    raise ConfigError(
                        f"Line {line_number}: {error}"
                    ) from None
    except (OSError, UnicodeError) as error:
        raise ConfigError(f"Cannot read '{filename}': {error}") from None

    missing = [key for key in REQUIRED_KEYS if key not in config]
    if missing:
        raise ConfigError(f"Missing mandatory keys: {', '.join(missing)}.")

    width = cast(int, config["WIDTH"])
    height = cast(int, config["HEIGHT"])
    for key in ("ENTRY", "EXIT"):
        x, y = cast(Tuple[int, int], config[key])
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(f"{key} must be inside the maze bounds.")
    if config["ENTRY"] == config["EXIT"]:
        raise ConfigError("ENTRY and EXIT must be different cells.")
    return config
