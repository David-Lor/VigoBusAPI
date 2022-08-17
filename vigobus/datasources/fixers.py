import re
from typing import Tuple

from roman import fromRoman
from roman import InvalidRomanNumeralError as NoRoman

__all__ = ("Fixers",)


class Fixers:

    class Const:
        prepositions = (
            "a", "de", "en", "por", "sin", "so", "do", "da", "dos", "das", "no", "na", "nos", "nas", "sen", "o", "a",
            "lo", "la", "los", "las", "os", "as", "y", "e", "del"
        )
        bus_line_letters = ('"A"', '"B"', '"C"', 'A   ', 'B   ', 'C   ', 'A ', 'B ', 'C ')
        """Line letters that external data sources return as part of the route; we set them as part of the line instead
        """

    @classmethod
    def stop_name(cls, original_name: str) -> str:

        # Remove double spaces
        name = re.sub(' +', ' ', original_name)

        # Replace - with commas
        name = name.replace("-", ",")

        # Force one space after each comma, remove unnecessary spaces before, remove duplicated commas
        name = name.replace(",", ", ").replace(" ,", ",").replace(", ,", ",")

        # Remove unnecessary commas just before parenthesis
        name = name.replace(", (", " (").replace(",(", " (")

        # Remove unnecessary dots after parenthesis
        name = name.replace(").", ")")

        # Remove unnecessary spaces after opening or before closing parenthesis
        name = name.replace("( ", "(").replace(") ", ")")

        # Capitalize each word on the name (if the word is at least 3 characters long);
        # Set prepositions to lowercase;
        # Fix chars
        # name_words = fix_chars(name).split()  # TODO Try to fix encoding other way
        name_words = name.split()
        for index, word in enumerate(name_words):
            # noinspection PyBroadException
            try:
                word = word.strip().lower()
                if word not in cls.Const.prepositions:
                    if word.startswith("("):
                        char = word[1]
                        word = word.replace(char, char.upper())
                    else:
                        word = word.capitalize()
                name_words[index] = word

            except Exception:
                pass

        name = ' '.join(name_words)

        # Turn roman numbers to uppercase
        name = ' '.join(word.upper() if cls.is_roman(word) else word for word in name.split())

        return name

    @classmethod
    def bus_line_route(cls, line: str, route: str) -> Tuple[str, str]:
        # Some routes have a letter that is part of the line in it, fix that:
        # Remove the letter from route and append to the end of the line instead
        for letter in cls.Const.bus_line_letters:
            if route.strip().startswith(letter):
                route = route.replace(letter, "")
                letter = letter.replace('"', "").replace(" ", "")
                line = line + letter
                break

        # Replace possible left double quote marks with simple quote marks
        # Remove asterisks on bus route
        line = line.replace('"', "'")
        route = route.replace('"', "'").replace("*", "")

        return line, route

    @classmethod
    def is_roman(cls, text: str) -> bool:
        """Check if the given string is a Roman number. Return True if it is, False if not.
        """
        text = text.strip().upper()
        text = re.sub(r'[^A-Z]', "", text)
        try:
            fromRoman(text)
        except NoRoman:
            return False
        return True
