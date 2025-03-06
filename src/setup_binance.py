import os
from dotenv import load_dotenv
from binance.spot import Spot as Client

load_dotenv()

class BinanceClient():

    _client = None

    @staticmethod
    def get_client():
        if BinanceClient._client is None:
            BinanceClient._client = Client(
                api_key= os.getenv('apikey'), 
                api_secret= os.getenv('secret')
            )
            return BinanceClient._client
        else:
            return BinanceClient._client