"""WSDL_CONST
Const variables related with the WSDL API & its endpoints
"""

HEADERS = {"content-type": "application/soap+xml; charset=utf-8"}

GET_STOP_BODY = """
    <?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
      <soap12:Body>
        <BuscarParadasIdParada xmlns="http://tempuri.org/">
          <IdParada>{stop_id}</IdParada>
        </BuscarParadasIdParada>
      </soap12:Body>
    </soap12:Envelope>
""".strip()

GET_BUSES_BODY = """
    <?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
      <soap12:Body>
        <EstimacionParadaIdParada xmlns="http://tempuri.org/">
          <IdParada>{stop_id}</IdParada>
        </EstimacionParadaIdParada>
      </soap12:Body>
    </soap12:Envelope>
""".strip()

GET_NEAR_STOPS_BODY = """
    <?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <BuscarParadas xmlns="http://tempuri.org/">
          <Latitud>{lat}</Latitud>
          <Longitud>{lon}</Longitud>
        </BuscarParadas>
      </soap:Body>
    </soap:Envelope>
""".strip()
