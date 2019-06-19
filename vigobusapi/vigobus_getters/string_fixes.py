"""STRING_FIXES
Functions that help fixing the Strings returned by the API.
"""

# # Native # #
import re
from typing import Tuple

# # Installed # #
from roman import fromRoman
from roman import InvalidRomanNumeralError as NoRoman

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
    "lo", "la", "los", "las", "os", "as", "y", "e"
)


def fix_stop_name(name: str) -> str:
    """Fix the Stop names given by the original data sources.
    """
    print("input:", name)
    # Capitalize each word on the name (if the word is at least 3 characters long);
    # Set prepositions to lowercase;
    # Fix chars
    name = ' '.join(
        word.capitalize() if word.strip().lower() not in PREPOSITIONS else word.lower()
        for word in fix_chars(name).split()
    )
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
    print("output:", name)
    return name


# List of the Line letters that the API returns as part of the route;
# We include them as part of the line instead
LINE_LETTERS = ('"A"', '"B"', '"C"', 'A   ', 'B   ', 'C   ', 'A ', 'B ', 'C ')


def fix_bus(line: str, route: str) -> Tuple[str, str]:
    """Fix the Bus lines and routes given by the original API.
    """
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
    return line, route


CHARS_FIXED = {  # {"WrongChar" : "FixedChar"}
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


def fix_chars(input_string: str) -> str:
    """Fix wrong characters from strings given by the WSDL API.
    Function will use the CHARS_FIXED dict {"WrongChar":"FixedChar"}
    """
    for wrong, fix in CHARS_FIXED.items():
        input_string = input_string.replace(wrong, fix)
    return input_string
