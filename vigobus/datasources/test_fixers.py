import pytest

from .fixers import Fixers


@pytest.mark.parametrize("line, route, expected_line, expected_route", [
    ("15", "C SAMIL por PI MARGALL", "15C", "SAMIL por PI MARGALL"),
    ("15", "B SAMIL por BEIRAMAR", "15B", "SAMIL por BEIRAMAR"),
    ("5", "\"B\" NAVIA por CASTELAO", "5B", "NAVIA por CASTELAO"),
])
def test_fix_bus_line_route(line, route, expected_line, expected_route):
    result_line, result_route = Fixers.bus_line_route(line, route)
    assert result_line == expected_line
    assert result_route == expected_route


@pytest.mark.parametrize("name, expected_name", [
    # TODO Update after implementing "Replace double spaces present before a number at the end, with a comma+space"
    # If expected_name=True, expect it to be equal to name
    ("Rúa de Jenaro de la Fuente  29", "Rúa de Jenaro de la Fuente 29"),
    ("Estrada de Moledo  6", "Estrada de Moledo 6"),
    ("Estrada de Moledo, 6", True),
    ("Rúa de Tomás Paredes  4", "Rúa de Tomás Paredes 4"),
    ("Rúa da Pedra Seixa (Colexio)", True),
    ("Rúa de Pi i Margall (fronte 5)", "Rúa de Pi i Margall (Fronte 5)"),
    ("Subida á Madroa (fronte Campo Fútbol)", "Subida á Madroa (Fronte Campo Fútbol)"),
    ("Rúa de Manuel Álvarez (fronte cruce Camiño Sulevada)", "Rúa de Manuel Álvarez (Fronte Cruce Camiño Sulevada)"),
    ("Estrada de Fragoselo (cruce Camiño Río da Barxa)", "Estrada de Fragoselo (Cruce Camiño Río da Barxa)"),
    ("Rúa Castañal (cruce Camiño das Presas)", "Rúa Castañal (Cruce Camiño das Presas)"),
    ("Rúa das Teixugueiras  19-Portal 5", "Rúa das Teixugueiras 19, Portal 5"),
    ("Rúa de Santo Amaro (Praza de España)", True),
    ("Rúa do Gaiteiro de Ricardo Portela (fronte Pavillón)", "Rúa do Gaiteiro de Ricardo Portela (Fronte Pavillón)"),
    ("Telecomunicacións (CUVI)", "Telecomunicacións (Universidade)"),
    ("Telecomunicacións (CUVI) B", "Telecomunicacións (Universidade) B"),
    ("Estrada de Camposancos (cruce Camiño da Estea)", "Estrada de Camposancos (Cruce Camiño da Estea)"),
    ("Paseo de Alfonso XII (Mirador)", True),
])
def test_fix_stop_name(name, expected_name):
    if expected_name is True:
        expected_name = name
    result_name = Fixers.stop_name(name)
    assert result_name == expected_name
