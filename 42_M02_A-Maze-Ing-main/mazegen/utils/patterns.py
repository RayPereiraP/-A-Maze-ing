from typing import TypedDict, Optional


class PatternDef(TypedDict):
    width: int
    height: int
    pattern: Optional[list[str]]


PATTERN_42 = [
    "1010111",
    "1010001",
    "1110111",
    "0010100",
    "0010111"
]

PATTERN_42_LOGO = [
    "000011011110",
    "000110010110",
    "001100000110",
    "011000001100",
    "111111011000",
    "111111011010",
    "000011011110",
    "000011000000",
    "000011000000"
]

PATTERN_HEART_SMALL = [
    "00110001100",
    "01111011110",
    "11111111111",
    "11111111111",
    "01111111110",
    "00111111100",
    "00011111000",
    "00001110000",
    "00000100000",
]

PATTERN_HEART_BIG = [
    "0011100011100",
    "0111110111110",
    "1111111111111",
    "1111111111111",
    "1111111111111",
    "0111111111110",
    "0011111111100",
    "0001111111000",
    "0000111110000",
    "0000011100000",
    "0000001000000",
]

PATTERN_DIAMOND = [
    "0111110",
    "1111111",
    "1111111",
    "0111110",
    "0011100",
    "0001000"
]

PATTERN_STAR = [
    "000000010000000",
    "000000111000000",
    "000001111100000",
    "001111111111100",
    "000111111111000",
    "000011111110000",
    "000111111111000",
    "001111111111100",
    "000001111100000",
    "000000111000000",
    "000000010000000",
]

PATTERN_TARGET = [
    "000000010000000",
    "000000010000000",
    "000000111000000",
    "000001111100000",
    "000011111110000",
    "011111111111110",
    "000011111110000",
    "000001111100000",
    "000000111000000",
    "000000010000000",
    "000000010000000",
]

PATTERN_CAT = [
    "00100001000000",
    "00110011000000",
    "00111111000000",
    "01111111100000",
    "01111111100000",
    "00111111000000",
    "00011110000000",
    "00111111000000",
    "00111111000000",
    "01111111100000",
    "01111111100000",
    "11111111110000",
    "11111111110001",
    "11111111110010",
    "11111111110010",
    "01111111100100",
    "00111111001000",
    "00000011110000",
]

PATTERNS: dict[str, PatternDef] = {

    "None": {
        "pattern": None,
        "width": 0,
        "height": 0,
    },

    "42": {
        "pattern": PATTERN_42,
        "width": len(PATTERN_42[0]),
        "height": len(PATTERN_42),
    },

    "42_logo": {
        "pattern": PATTERN_42_LOGO,
        "width": len(PATTERN_42_LOGO[0]),
        "height": len(PATTERN_42_LOGO),
    },

    "heart": {
        "pattern": PATTERN_HEART_SMALL,
        "width": len(PATTERN_HEART_SMALL[0]),
        "height": len(PATTERN_HEART_SMALL),
    },

    "heart_big": {
        "pattern": PATTERN_HEART_BIG,
        "width": len(PATTERN_HEART_BIG[0]),
        "height": len(PATTERN_HEART_BIG),
    },

    "diamond": {
        "pattern": PATTERN_DIAMOND,
        "width": len(PATTERN_DIAMOND[0]),
        "height": len(PATTERN_DIAMOND),
    },
    "star": {
        "pattern": PATTERN_STAR,
        "width": len(PATTERN_STAR[0]),
        "height": len(PATTERN_STAR),
    },

    "target": {
        "pattern": PATTERN_TARGET,
        "width": len(PATTERN_TARGET[0]),
        "height": len(PATTERN_TARGET),
    },

    "cat": {
        "pattern": PATTERN_CAT,
        "width": len(PATTERN_CAT[0]),
        "height": len(PATTERN_CAT),
    }
}
