from src.setup_binance import BinanceClient
import pandas as pd
import time

def map_to_chunks(lookback: int, chunk_size: int = 1000):
    # Create an empty list to store the result
    map_chunks = []
    
    # Calculate the number of chunks
    start = 0
    while start < lookback:
        end = min(start + chunk_size, lookback)  # Ensure the 'end' does not exceed 'a'
        map_chunks.append({'startLookback': start, 'endLookback': end})
        start = end  # Update start for the next chunk
    return map_chunks

def parse_data_to_df(data: list):

    df = pd.DataFrame(
        data, 
        columns= [
            'open_time', 
            'open', 
            'high', 
            'low', 
            'close', 
            'volume', 
            'close_time', 
            'quote_asset_volume', 
            'number_of_trades', 
            'taker_buy_base_asset_volume', 
            'taker_buy_quote_asset_volume', 
            'ignore'
        ]
    )

    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df = df.drop('ignore', axis=1)
    df = df.astype(
        {
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'volume': 'float64',
            'quote_asset_volume': 'float64',
            'number_of_trades': 'int64',
            'taker_buy_base_asset_volume': 'float64',
            'taker_buy_quote_asset_volume': 'float64'
        }
    )

    return df

def get_historical_data(
        coin: str, 
        lookback: int, 
    ):

    df = pd.DataFrame()

    client = BinanceClient.get_client()

    map_chunks = map_to_chunks(lookback)
    today = int(time.time() * 1000)

    for chunk in map_chunks:
        # Define the end time as the current time (the latest time)
        end_time = today - (chunk['startLookback'] * 24 * 60 * 60 * 1000)
        # Calculate the start time
        start_time = today - (chunk['endLookback'] * 24 * 60 * 60 * 1000)

        status = client.klines(
            symbol=coin, 
            limit=1000, 
            interval='1d',
            startTime=start_time,
            endTime=end_time
        )
        df_chunk = parse_data_to_df(status)
        df = pd.concat([df, df_chunk], axis=0)

    
    df = df[['open_time', 'close']]
    df = df.sort_values(by='open_time', ascending=True)
    df = df.rename(
        columns = {
            'open_time': 'date',
            'close': coin
        }
    )
    return df.reset_index(drop=True)