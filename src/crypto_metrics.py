from src.get_historical_data import get_historical_data
from src.get_treasury_rate import get_treasury_rate
import pandas as pd
import numpy as np

class CryptoMetrics:

    def __init__(self, lookback) -> None:
        self.lookback = lookback

    def calculate_rsi(
            self, 
            df: pd.DataFrame, 
            coin: str, 
            PERIOD = 14
        ) -> pd.DataFrame:
        """
        Calculates the Relative Strength Index (RSI) for a specified column 
        in a DataFrame.
        The RSI is a momentum oscillator that measures the speed and change 
        of price movements, typically used to identify overbought or oversold 
        conditions in a market.

        ---------
        Parameters
        ----------
        - df (pd.DataFrame): DataFrame containing historical price data.
        - coin (pd.DataFrame): Coin that is being evaluated for calculations.
        - period (int, optional): The period over which the RSI is calculated. 
        Defaults to 14.
        ----------
        Returns
        ----------
        - pd.DataFrame: A Series containing the RSI values for the 
        specified coin.
        """


        df_rsi = df.copy()

        delta = df_rsi[coin].diff()

        # Calculate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate rolling averages
        avg_gain = gain.rolling(window=PERIOD, min_periods=1).mean()
        avg_loss = loss.rolling(window=PERIOD, min_periods=1).mean()
        
        # Calculate RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df_rsi[f'rsi_{coin}'] = rsi
        df_rsi[f'rsi_buy_{coin}'] = (
            np.where(df_rsi[f'rsi_{coin}'] < 30, 1, 0)
        )

        df_rsi[f'rsi_sell_{coin}'] = (
            np.where(df_rsi[f'rsi_{coin}'] > 70, 1, 0)
        )

        df_rsi.reset_index(drop=True,inplace=True)
        return df_rsi


    def calculate_corr_treasury(
            self, 
            df: pd.DataFrame,
            coin: str,
            PERIOD=90, 
        ) -> pd.DataFrame:
        """
        This function computes the correlation between the price of a coin 
        and the monthly treasury rate, using historical data.

        ---------
        Parameters
        ----------
        - df (pd.DataFrame): DataFrame containing historical price data 
        of the coin selected.
        - period (int, optional): The time period (in days) over which the 
        correlation is computed. Defaults to 90 days.
        ----------
        Returns
        ----------
        - pd.DataFrame: Correlation values between the coin price and 
        the monthly treasury rate over the specified period with buy and sell
        signals, based on a threshold set.
        """
        df_corr_treasury = df.copy()

        treasury_data = get_treasury_rate(lookback=self.lookback)
        df_corr_treasury = df_corr_treasury.merge(
            treasury_data, 
            on='date', 
            how='left'
        )
        df_corr_treasury['treasury_rate'] = (
            df_corr_treasury['treasury_rate'].ffill()
        )

        df_corr_treasury[f'treasury_corr_{coin}'] = (
            df_corr_treasury[coin].rolling(
            window=PERIOD
            ).corr(
                df_corr_treasury['treasury_rate'])
        )
        
        # Puts a correlation threshold of -0.7 and 0.7 for buy and sell signals
        df_corr_treasury[f"treasury_corr_buy_{coin}"] = (
            df_corr_treasury[f"treasury_corr_{coin}"] < -0.7
        )

        df_corr_treasury[f"treasury_corr_sell_{coin}"] = (
            df_corr_treasury[f"treasury_corr_{coin}"] > 0.7
        )

        df_corr_treasury.reset_index(drop=True,inplace=True)
        return df_corr_treasury


    def calculate_bollinger_bands(
            self, 
            df: pd.DataFrame,
            coin: str,
            PERIOD=15, 
            STD_FACTOR=1.5,
        ) -> pd.DataFrame:
        """
        Calculates the Bollinger Bands metric.

        ---------
        Parameters
        ----------
        - df (pd.DataFrame): DataFrame containing the price data.
        - PERIOD (int): Number of days to look back and track the 
        Bollinger Bands.
        - STD_FACTOR (float): Standard deviation factor used to generate the 
        bands.
        ----------
        Returns
        ----------
        - pd.DataFrame: DataFrame with the Bollinger Bands metric for the coin
        evaluated, buy and sell signals for that period as well, based on the
        STD_FACTOR selected as threshold.
        """

        df_bb = df.copy()

        df_bb[f'std_{coin}'] = (
            df_bb[coin].rolling(PERIOD, min_periods=1).std()
        )
        df_bb[f'mean_{coin}'] = df_bb[coin].rolling(
            PERIOD, min_periods=1
        ).mean()

        # Criação das Bandas de Bollinger
        df_bb[f'top_band_{coin}'] = (
            df_bb[f'mean_{coin}'] + df_bb[f'std_{coin}'] * STD_FACTOR
        )
        
        df_bb[f'bottom_band_{coin}'] = (
            df_bb[f'mean_{coin}'] - df_bb[f'std_{coin}'] * STD_FACTOR
        )

        # Inicialização da coluna de compra
        df_bb[f'bb_buy_{coin}'] = np.where(
            df_bb[coin] < df_bb[f'bottom_band_{coin}'], 
            1, 
            0,
        )

        # Inicialização da coluna de compra
        df_bb[f'bb_sell_{coin}'] = np.where(
            df_bb[coin] > df_bb[f'top_band_{coin}'], 
            1, 
            0,
        )

        df_bb.reset_index(drop=True,inplace=True)

        return df_bb
    

    def calculate_macd(
            self,
            df: pd.DataFrame,
            coin: str,
            short_window = 12, 
            long_window = 26, 
            signal_window = 9
            ) -> pd.DataFrame:
        
        """
        Calculates the mean average convergence divergence metric, based on
        market fluctuation.
        
        ---------
        Parameters
        ----------
        - df (pd.DataFrame): DataFrame containing the price data.
        - short_window (int): number of days to lookback and track EMA
        - long_window (int): number of days to lookback and track EMA
        - signal_window (): number of days to calulate signal line
        ----------
        Returns
        ---------
        - pd.DataFrame: DataFrame with MACD metric for each metal.
        """
        df_macd = df.copy()

        # Calculate EMAs (exponential moving average):
        df_macd[f'EMA{short_window}_{coin}'] = df_macd[coin].ewm(
            span = short_window, 
            adjust=False
        ).mean()
        
        df_macd[f'EMA{long_window}_{coin}'] = df_macd[coin].ewm(
            span = long_window,
            adjust=False
        ).mean()

        # Calculate MACD
        df_macd[f'MACD_{coin}'] = (
            df_macd[f'EMA{short_window}_{coin}'] - df_macd[f'EMA{long_window}_{coin}']
        )

        # Calculate signal line
        df_macd[f'Signal_Line_{coin}'] = df_macd[f'MACD_{coin}'].ewm(
            span = signal_window, 
            adjust=False
        ).mean()

        # Generate buy and sell signals
        df_macd[f'MACD_buy_{coin}'] = (
            np.where( 
                (df_macd[f'MACD_{coin}'] > df_macd[f'Signal_Line_{coin}']) & 
                (df_macd[f'MACD_{coin}'].shift(1) <= df_macd[f'Signal_Line_{coin}'].shift(1)), 
                1, 
                0
            )
        )

        df_macd[f'MACD_sell_{coin}'] = (
            np.where(
                (df_macd[f'MACD_{coin}'] < df_macd[f'Signal_Line_{coin}']) & 
                (df_macd[f'MACD_{coin}'].shift(1) >= df_macd[f'Signal_Line_{coin}'].shift(1)), 
                1,
                0
            )
        )


        df_macd.reset_index(drop=True,inplace=True)
        return df_macd 


    def calculate_trendline(
            self, 
            df: pd.DataFrame, 
            period = 'W'
        ) -> pd.DataFrame:
        """
        Generates the necessary columns for plotting the trendline graph.

        ---------
        Parameters
        ----------
        - df (pd.DataFrame): DataFrame containing the price data.
        - period (str): Period string aliases from Pandas. 
        The list of possible aliases can be found 
        here: https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-period-aliases
        ----------
        Returns
        ----------
        - pd.DataFrame: DataFrame with the necessary columns to plot trendline graphs.
        """
        # Add columns for weekly min max values. 
        df_trendline = df.copy()
        df_trendline['periodo'] = df_trendline['data'].dt.to_period(
            period
        ).dt.start_time
        
        # Calculate weekly min max values.
        max_periodo = df_trendline.groupby('periodo').max().add_suffix('_max')
        min_periodo = df_trendline.groupby('periodo').min().add_suffix('_min')

        df_trendline = df_trendline.merge(max_periodo, on='periodo', how='left')
        df_trendline = df_trendline.merge(min_periodo, on='periodo', how='left')

        df_trendline.drop(
            columns = [
                'periodo',
                'data_min', 
                'data_max'
            ], 
            inplace=True
        )
        df_trendline.reset_index(drop=True,inplace=True)
        return df_trendline
    
    def calculate_volatility(self, df: pd.DataFrame, window=15) -> pd.DataFrame:
        """
        Calculates the volatility of each metal commodity for the given window
        period.
        
        ---------
        Parameters
        ----------
        - df (pd.DataFrame): DataFrame containing the price data.
        - window (int): number of days to lookback and calculate volatility.
        ----------
        Returns
        ---------
        - pd.DataFrame: DataFrame with volatility for each metal.
        """

        df_volatility = df.copy()
        metals = df.select_dtypes(
            include=['float64', 'int64']
        ).columns.tolist()

        metals.remove('dolar')
        
        for metal in metals:
            df_volatility[f'retorno_diario_{metal}'] = df_volatility[
                metal
            ].pct_change(fill_method = None)
            df_volatility[f'volatilidade_{metal}'] = df_volatility[
                f'retorno_diario_{metal}'
            ].rolling(window=window).std() * 100
        
        df_volatility.reset_index(drop=True,inplace=True)
        return df_volatility
    
    
    def set_buy(self, df: pd.DataFrame, coin: str, THRESHOLD=0.5) -> pd.DataFrame:
        """
        Performs the calculation to set a buy indication, based on
        weights criteria.
        ---------
        Parameters
        ----------
        - dataframes (list): List of DataFrames containing the calculated 
        metrics.
        - THRESHOLD (float): threshold to set a buy indication.
        ----------
        Returns
        ---------
        - pd.DataFrame: DataFrame with buy indication and dates.
        """

        weights = {
            'rsi' : 0.4,
            'treasury_corr' : 0.1,
            'bb' : 0.3,
            'MACD' : 0.1,
        }

        rsi = self.calculate_rsi(df, coin)
        treasury_corr = self.calculate_corr_treasury(df, coin)
        bb = self.calculate_bollinger_bands(df, coin)
        MACD = self.calculate_macd(df, coin)

        dataframes = [rsi, treasury_corr, bb, MACD]

        df_compiled = pd.concat(dataframes, axis=1)
        df_compiled = df_compiled.loc[:, ~df_compiled.columns.duplicated()]

        df_compiled[f'metric_buy_{coin}'] = (
            df_compiled[f'rsi_buy_{coin}']*weights['rsi'] + 
            df_compiled[f'treasury_corr_buy_{coin}']*weights['treasury_corr'] + 
            df_compiled[f'bb_buy_{coin}']*weights['bb'] +
            df_compiled[f'MACD_buy_{coin}']*weights['MACD']
        )
        df_compiled[f'buy_{coin}'] = np.where(
            df_compiled[f'metric_buy_{coin}'] > THRESHOLD,
            1,
            0
        )

        df_compiled[f'metric_sell_{coin}'] = (
            df_compiled[f'rsi_sell_{coin}']*weights['rsi'] + 
            df_compiled[f'treasury_corr_sell_{coin}']*weights['treasury_corr'] + 
            df_compiled[f'bb_sell_{coin}']*weights['bb'] +
            df_compiled[f'MACD_sell_{coin}']*weights['MACD']
        )

        df_compiled[f'sell_{coin}'] = np.where(
            df_compiled[f'metric_sell_{coin}'] > THRESHOLD,
            1,
            0
        )

        df_compiled = df_compiled[['date', coin, f'buy_{coin}', f'sell_{coin}']]
        df_compiled.reset_index(drop=True,inplace=True)
        
        return df_compiled