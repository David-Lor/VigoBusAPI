"""STRING_FIXES
Functions that help fixing the Strings returned by the API.
"""

# # Native # #
import re
from typing import Tuple

# # Installed # #
from roman import fromRoman
from roman import InvalidRomanNumeralError as NoRoman

__all__ = ("fix_stop_name", "fix_bus", "fix_chars")


def is_roman(text: str) -> bool:
    """Check if the given string is a Roman number.
    :param text: String to test (should be a single word, previously split)
    :type text: str
    :return: True if is roman number, False if is not
    :rtype: bool
    """
    try:
        fromRoman(text.strip().upper())
    except NoRoman:
        return False
    else:
        return True


def fix_stop_name(name: str) -> str:
    """Fix the Stop names given by the original API.
    :param name: original Stop name
    :type name: str
    :return: fixed Stop name
    :rtype: str
    """
    # Capitalize each word on the name (if the word is at least 3 characters long)
    name = ' '.join(word.capitalize() if len(word) > 2 else word for word in fix_chars(name).split())
    # Replace - with commas
    name = name.replace("-", ",")
    # Force one space after each comma
    name = name.replace(",", ", ")
    # Remove double spaces
    name = re.sub(' +', ' ', name)
    # Remove unneeded commas just before parenthesis
    name = name.replace(", (", " (").replace(",(", " (")
    # Remove unneeded dots after parenthesis
    name = name.replace(").", ")")
    # Turn roman numbers to uppercase
    name = ' '.join(word.upper() if is_roman(word) else word for word in name.split())
    # Replace possible left double quote marks with simple quote marks
    return name


# List of the Line letters that the API returns as part of the route;
# We include them as part of the line instead
LINE_LETTERS = ('"A"', '"B"', '"C"', 'A   ', 'B   ', 'C   ', 'A ', 'B ', 'C ')


def fix_bus(line: str, route: str) -> Tuple[str, str]:
    """Fix the Bus lines and routes given by the original API.
    :param line: original Bus line string returned by API
    :param route: original Bus route string returned by API
    :type line: str
    :type route: str
    :return: tuple (line, route), both as strings fixed
    :rtype: str, str
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
    :param input_string: the string to be fixed (required)
    :type input_string: str
    :return: the given string with wrong chars fixed
    :rtype: str
    """
    for wrong, fix in CHARS_FIXED.items():
        input_string = input_string.replace(wrong, fix)
    return input_string
