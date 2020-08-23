"""UNIT TEST - HTML Parser
Test functions from vigobus_getters.html.html_parser
"""

# # Installed # #
import pytest

# # Project # #
from vigobusapi.vigobus_getters.html.html_parser import clear_duplicated_buses
from vigobusapi.entities import Bus

BUS_A = {"line": "A", "route": "A"}
BUS_B = {"line": "B", "route": "B"}
BUS_C = {"line": "C", "route": "C"}


@pytest.mark.parametrize("buses,expected_buses", [
    (
        # Input Buses
        [
            Bus(**BUS_A, time=0),
            Bus(**BUS_A, time=1),
            Bus(**BUS_A, time=1),  # should be removed
            Bus(**BUS_A, time=2),

            Bus(**BUS_B, time=10),
            Bus(**BUS_B, time=11),

            Bus(**BUS_C, time=2),
            Bus(**BUS_C, time=2),  # should be removed
            Bus(**BUS_C, time=2),  # should be removed
            Bus(**BUS_C, time=3),
        ],
        # Expected Buses
        [
            Bus(**BUS_A, time=0),
            Bus(**BUS_A, time=1),
            Bus(**BUS_A, time=2),

            Bus(**BUS_B, time=10),
            Bus(**BUS_B, time=11),

            Bus(**BUS_C, time=2),
            Bus(**BUS_C, time=3),
        ]
    )
])
def test_clear_duplicated_buses(buses, expected_buses):
    result = clear_duplicated_buses(buses)
    sorter = lambda _bus: (_bus.line, _bus.time)
    assert sorted(result, key=sorter) == sorted(expected_buses, key=sorter)
