"""HTML_CONST
Const variables related with the HTML data source
"""

# # # # #
# # Request-related variables
# # # # #

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'accept-encoding': 'accept-encoding',
    'accept-language': 'es,en-US;q=0.7,en;q=0.3',
    'content-type': 'application/x-www-form-urlencoded',
    'dnt': '1',
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'
}
"""Headers to be used on requests"""

EXTRA_DATA_REQUIRED = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
"""Extra Data fields that must be fetched from the HTML source code, and used on the EXTRA_DATA str as placeholders"""

EXTRA_DATA = "__EVENTTARGET=GridView1&__VIEWSTATE={__VIEWSTATE}&__VIEWSTATEGENERATOR={__VIEWSTATEGENERATOR}"\
             "&__EVENTVALIDATION={__EVENTVALIDATION}&__EVENTARGUMENT=Page%24{page}"
"""Extra Data that must be sent as part of the POST request to the HTML data source, when getting a certain page;
the placeholded values must be formatted with the values fetched from the HTML source code
"""

EXTRA_DATA_PAGE = "page"
"""This variable is used as a placeholder on EXTRA_DATA to set the page number"""

# # # # #
# # Generic parsing variables
# # # # #

HTML_PARSER = "html.parser"

# # # # #
# # Parsers for Stop (kwargs for html.find/find_all)
# # # # #

PARSER_STOP_ID = {
    "name": "span",
    "attrs": {
        "id": "lblParada"
    }
}

PARSER_STOP_NAME = {
    "name": "span",
    "attrs": {
        "id": "lblNombre"
    }
}

# # # # #
# # Parsers for Buses (kwargs for html.find/find_all)
# # # # #

# Table that contains all the buses
PARSER_BUSES_TABLE = {
    "name": "table",
    "attrs": {
        "id": "GridView1"
    }
}

# Table Rows, each one being an bus, containing 3 <td> with the bus info (line, route, time)
# Two different types of rows
PARSERS_BUSES_ROWS_INSIDE_TABLE = [
    {
        "name": "tr",
        "attrs": {
            "style": "color:#333333;background-color:#F7F6F3;"
        }
    },
    {
        "name": "tr",
        "attrs": {
            "style": "color:#284775;background-color:White;"
        }
    }
]

# # # # #
# # Parsers for Page Numbers (kwargs for html.find/find_all)
# # # # #

# Table that contains all the page numbers
PARSER_PAGE_NUMBERS_TABLE = {
    "name": "tr",
    "attrs": {
        "align": "center",
        "style": "color:White;background-color:#284775;"
    }
}

# All linked page numbers inside table
PARSER_PAGE_NUMBERS_LINKED_INSIDE_TABLE = {
    "name": "a",
    "attrs": {
        "style": "color:White;"
    }
}

# Current page number inside table
PARSER_PAGE_NUMBER_CURRENT_INSIDE_TABLE = {
    "name": "span"
}
