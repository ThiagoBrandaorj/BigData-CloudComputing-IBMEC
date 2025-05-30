import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3979
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    # URL da API hospedada no Azure
    API_BASE_URL = "https://ibmec-ecommerce-produtos-thpedu-hpgdamgyc3c4grgx.centralus-01.azurewebsites.net"
