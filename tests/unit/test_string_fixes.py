"""UNIT TEST - String Fixes
Test functions from vigobus_getters.string_fixes
"""

# # Installed # #
import pytest

# # Project # #
from vigobusapi.vigobus_getters.string_fixes import fix_stop_name, fix_bus


@pytest.mark.parametrize("name,expected", [
    ("ROSALIA DE CASTRO-  69", "Rosalia de Castro, 69"),
    ("Rua S. Cristobo-(Subida a Madroa)", "Rua S. Cristobo (Subida a Madroa)"),
    ("PASEO DE ALFONSO XII-15", "Paseo de Alfonso XII, 15")
])
def test_fix_stop_name(name, expected):
    result = fix_stop_name(name)
    assert result == expected


@pytest.mark.parametrize("line,route,expected_line,expected_route", [
    ("15", "C SAMIL por PI MARGALL", "15C", "SAMIL por PI MARGALL"),
    ("15", "B SAMIL por BEIRAMAR", "15B", "SAMIL por BEIRAMAR"),
    ("5", "\"B\" NAVIA por CASTELAO", "5B", "NAVIA por CASTELAO")
])
def test_fix_bus(line, route, expected_line, expected_route):
    result_line, result_route = fix_bus(line=line, route=route)
    assert result_line == expected_line
    assert result_route == expected_route
