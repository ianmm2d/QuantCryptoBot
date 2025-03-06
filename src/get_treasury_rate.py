import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_treasury_rate(lookback: int) -> pd.DataFrame:

    """
    Retrieves the value of treasury bill in the last 13 weeks
    Parameters
    ----------
    months: quantity of months to look back
    """

    TICKER = '^IRX'

    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback)
    
    try:
        data = yf.download(
            tickers = TICKER,
            start=start_date,
            end=end_date
        )
        data = data[('Close', '^IRX')]
        data = data.rename('treasury_rate')
        data = data.reset_index()
        data = data.rename(
            columns = {
                'Date' : 'date'
            }
        )
    except Exception as e:
        print(f"An error occured: {e}")
        return pd.DataFrame()
    
    return data