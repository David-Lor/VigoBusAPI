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
    'dnt': '1',
    'connection': 'keep-alive',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'
}
"""Headers to be used on requests"""

HEADERS_NEXT_LOADS = {
    'content-type': 'application/x-www-form-urlencoded',
    'referer': None
}
"""Additional Headers to be used on more page loads after first page.
Referer is the HTML data source URL + the formatted HEADERS_NEXT_LOADS_REFERER_PARAMS"""

HEADERS_NEXT_LOADS_REFERER = "referer"
"""Key for the referer Header"""

HEADERS_NEXT_LOADS_REFERER_PARAMS = "?parada={stopid}"
"""Value for the 'referer' key on HEADERS_NEXT_LOADS; 'stopid' is a placeholder so the string must be formatted"""

EXTRA_DATA_REQUIRED = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
"""Extra Data fields that must be fetched from the HTML source code, and used on the EXTRA_DATA str as placeholders"""

EXTRA_DATA = "__EVENTTARGET=GridView1&__EVENTARGUMENT=Page%24{page}&__VIEWSTATE={__VIEWSTATE}&"\
             "__VIEWSTATEGENERATOR={__VIEWSTATEGENERATOR}&__EVENTVALIDATION={__EVENTVALIDATION}"
"""Extra Data that must be sent as body of the POST request to the HTML data source, when getting a certain page;
the placeholded values must be formatted with the values fetched from the HTML source code
"""

EXTRA_DATA_PAGE = "page"
"""This variable is used as a placeholder on EXTRA_DATA to set the page number"""

# USER_AGENTS = (
#     "Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/62.0.3202.84 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
#     "Chrome/60.0.3112.107 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 7.0; SM-G930VC Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
#     "Chrome/58.0.3029.83 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0"
#     " Chrome/55.0.2883.91 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/52.0.2743.98 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/47.0.2526.83 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/47.0.2526.83 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 7.1.1; G8231 Build/41.2.A.0.219; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0.1; E6653 Build/32.2.A.0.253) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/52.0.2743.98 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0; HTC One X10 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Version/4.0 Chrome/61.0.3163.98 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/52.0.2743.98 Mobile Safari/537.3",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 "
#     "Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
#     "CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/13.2b11866"
#     " Mobile/16A366 Safari/605.1.15",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 "
#     "Mobile/15A372 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 "
#     "Mobile/15A5341f Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 "
#     "Mobile/15A5370a Safari/604.1",
#     "Mozilla/5.0 (iPhone9,3; U; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) "
#     "Version/10.0 Mobile/14A403 Safari/602.1",
#     "Mozilla/5.0 (iPhone9,4; U; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) "
#     "Version/10.0 Mobile/14A403 Safari/602.1",
#     "Mozilla/5.0 (Apple-iPhone7C2/1202.466; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) "
#     "Version/3.0 Mobile/1A543 Safari/419.3 "
# )
# """List of user agents to random.choice"""

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
