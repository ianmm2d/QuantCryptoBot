from crypto_metrics import Metrics
from crypto_metrics import Predictions
from src.scrapping import generate_dataframe
from src.post_sheets import post_dataframe_to_google_sheets, clean_dataframes
from datetime import datetime, timedelta

def main():
    """
    Compiles every metric and posts into a Google Sheets file
    """
    MONTHS = 12*8
    PERIOD = 10
    LOOKBACK = 365
    
    metrics = Metrics(months=MONTHS)
    start_date = datetime.now() - timedelta(days=LOOKBACK)

    print('Starting the Scrapping')
    df = generate_dataframe(months=MONTHS)
    # Generates the prediction
    predictor = Predictions(df=df.loc[df['data'] > start_date])
    prediction = predictor.make_predictions()
    
    # Buying indications
    df = metrics.generate_quarter(df=df)
    rsi = metrics.calculate_rsi(df=df, PERIOD = PERIOD)
    corr_usd = metrics.calculate_corr_usd(df=df, PERIOD = PERIOD)
    corr_treasury = metrics.calculate_corr_treasury(df = df, PERIOD = PERIOD)
    bollinger_bands = metrics.calculate_bollinger_bands(df=df, PERIOD = PERIOD)
    macd = metrics.calculate_macd(df=df)
    
    # Visualization Support Tables 
    trendlines = metrics.calculate_trendline(df=df, period='W')
    volatility = metrics.calculate_volatility(df=df, window = 15)
    itens = metrics.calculate_itens_metal(df=df)

    # Compilation for buying option:
    dataframes = [df, rsi, corr_usd, corr_treasury, bollinger_bands, macd]
    compilated = metrics.set_buy(dataframes=dataframes)

    columns_to_drop = [
        'cobre', 
        'zinco', 
        'aluminio', 
        'chumbo', 
        'estanho', 
        'niquel', 
        'latao', 
        'dolar'
    ]

    # Prepare the DataFrames by dropping unnecessary columns
    rsi = rsi.drop(columns=columns_to_drop, axis=1, errors='ignore')
    corr_usd = corr_usd.drop(columns=columns_to_drop, axis=1, errors='ignore')
    corr_treasury = corr_treasury.drop(columns=columns_to_drop, axis=1, errors='ignore')
    bollinger_bands = bollinger_bands.drop(columns=columns_to_drop, axis=1, errors='ignore')
    macd = macd.drop(columns=columns_to_drop, axis=1, errors='ignore')
    trendlines = trendlines.drop(columns=columns_to_drop, axis=1, errors='ignore')
    volatility = volatility.drop(columns=columns_to_drop, axis=1, errors='ignore')
    compilated = compilated.drop(columns=columns_to_drop, axis=1, errors='ignore')
    
    compile = {
        'data' : df,
        'rsi' : rsi,
        'corr_usd' : corr_usd,
        'corr_treasury' : corr_treasury,
        'bollinger_bands': bollinger_bands,
        'macd' : macd,
        'trendlines': trendlines,
        'volatility' : volatility,
        'compilation' : compilated,
        'predictions': prediction,
        'itens': itens,
    }

    print('Starting to post on Google Sheets')
    for sheet, df in compile.items():
        print(sheet)
        df = clean_dataframes(dataframe=df)
        post_dataframe_to_google_sheets(
            dataframe = df,
            spreadsheet_name = 'compilation_sheet',
            sheet_name = sheet
        )
    print('This is the end.')

    return

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")