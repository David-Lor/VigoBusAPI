"""STRING_FIXES
Functions that help fixing the Strings returned by the API.
"""

# # Native # #
import re
from typing import Tuple

# # Installed # #
from roman import fromRoman
from roman import InvalidRomanNumeralError as NoRoman

# # Project # #
from vigobusapi.logger import logger

__all__ = ("fix_stop_name", "fix_bus")


def is_roman(text: str) -> bool:
    """Check if the given string is a Roman number. Return True if it is, False if not.
    """
    try:
        fromRoman(text.strip().upper())
    except NoRoman:
        return False
    else:
        return True


PREPOSITIONS = (
    "a", "de", "en", "por", "sin", "so", "do", "da", "dos", "das", "no", "na", "nos", "nas", "sen", "o", "a",
    "lo", "la", "los", "las", "os", "as", "y", "e", "del"
)
"""Prepositions will not be capitalized"""


def fix_stop_name(name: str) -> str:
    """Fix the Stop names given by the original data sources.
    """
    with logger.contextualize(stop_name_original=name):
        logger.debug("Fixing stop name")

        # Capitalize each word on the name (if the word is at least 3 characters long);
        # Set prepositions to lowercase;
        # Fix chars
        name_words = fix_chars(name).split()
        for index, word in enumerate(name_words):
            word = word.strip().lower()
            if word not in PREPOSITIONS:
                if word.startswith("("):
                    char = word[1]
                    word = word.replace(char, char.upper())
                else:
                    word = word.capitalize()
            name_words[index] = word
        name = ' '.join(name_words)

        # Replace - with commas
        name = name.replace("-", ",")

        # Force one space after each comma
        name = name.replace(",", ", ")

        # Remove double spaces
        name = re.sub(' +', ' ', name)

        # Remove unnecessary commas just before parenthesis
        name = name.replace(", (", " (").replace(",(", " (")

        # Remove unnecessary dots after parenthesis
        name = name.replace(").", ")")

        # Turn roman numbers to uppercase
        name = ' '.join(word.upper() if is_roman(word) else word for word in name.split())

        logger.bind(stop_name_fixed=name).debug("Fixed stop name")
        return name


LINE_LETTERS = ('"A"', '"B"', '"C"', 'A   ', 'B   ', 'C   ', 'A ', 'B ', 'C ')
"""Line letters that external data sources return as part of the route; we set them as part of the line instead"""


def fix_bus(line: str, route: str) -> Tuple[str, str]:
    """Fix the Bus lines and routes given by the original API.
    """
    with logger.contextualize(bus_line_original=line, bus_route_original=route):
        logger.debug("Fixing bus line & route")

        # ROUTE: just fix chars
        route = fix_chars(route)

        # LINE:
        # Some routes have a letter that is part of the line in it, fix that:
        # Remove the letter from route and append to the end of the line instead
        for letter in LINE_LETTERS:
            if route.strip().startswith(letter):
                route = route.replace(letter, "")
                letter = letter.replace('"', "").replace(" ", "")
                line = line + letter
                break

        # Replace possible left double quote marks with simple quote marks
        # Remove asterisks on bus route
        line = line.replace('"', "'")
        route = route.replace('"', "'").replace("*", "")

        # Final strip on line and route
        line = line.strip()
        route = route.strip()

        logger.bind(bus_line_fixed=line, bus_route_fixed=route).debug("Fixed bus line & route")
        return line, route


CHARS_FIXED = {
    "Ã": "Á",
    "Ã¡": "á",
    "Ã‰": "É",
    "Ã©": "é",
    "Ã": "Í",
    "Ã­": "í",
    "Ã“": "Ó",
    "Ã³": "ó",
    "Ãš": "Ú",
    "Ãº": "ú",
    "Ã‘": "Ñ",
    "Ã±": "ñ",
    "Â¿": "¿"
}
"""{WrongChar : FixedChar}"""


def fix_chars(input_string: str) -> str:
    """Fix wrong characters from strings.
    Function will use the CHARS_FIXED dict {"WrongChar":"FixedChar"}
    """
    # TODO Deprecate? (was only required for WSDL?)
    for wrong, fix in CHARS_FIXED.items():
        input_string = input_string.replace(wrong, fix)
    return input_string
