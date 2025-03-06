import pandas as pd


def format_output(
        initial_capital: float, 
        coint_holdings: float,
        final_price: float,
        total_invested: float,
        final_balance: float
    ) -> dict:
    
    return {
        "initial_capital": initial_capital,
        "coin_holdings": coint_holdings,
        "coin_holdings_dollars": coint_holdings*final_price,
        "total_invested": total_invested,
        "final_balance": final_balance
    }

def simulate_model_trader(
        df: pd.DataFrame, 
        initial_capital: float, 
        trade_value: float, 
        coin: str,
        verbose: bool = True
    ) -> float:

    balance = initial_capital  # Initial money in USD
    coin_holdings = 0  # Number of coins owned
    total_invested = 0  # Total money invested
    final_balance = 0  # Final balance after simulation
    final_price = df[coin].iloc[-1]  # Final price of the coin

    for _, row in df.iterrows():
        price = row[coin]  # Get current coin price

        if balance < 0:
            final_balance = balance + (coin_holdings * final_price)
            total_invested = initial_capital - balance
            if verbose:
                print("No more money to invest!")
                print(f"Initial Capital: ${initial_capital:.2f}")
                print(f"Coin Holdings in BTC: {coin_holdings:.8f}")
                print(f"Coin Holdings in dollars: ${coin_holdings*final_price:.2f}")            
                print(f"Total Invested: ${total_invested:.2f}")
                print(f"Final Balance: ${final_balance:.2f}")
            return format_output(
                initial_capital= initial_capital, 
                coint_holdings= coin_holdings, 
                final_price = final_price, 
                total_invested = total_invested, 
                final_balance = final_balance
            )
        
        # Sell logic: Sell all holdings when a sell signal appears
        if row[f'sell_{coin}'] == 1 and coin_holdings > 0:
            coins_sold = trade_value / price  # Sell coins based on trade value
            if coins_sold > coin_holdings:  # Prevent selling more than possible
                coins_sold = coin_holdings
            coin_holdings -= coins_sold
            balance += coins_sold * price


        # Buy logic: Buy $10 worth of the coin when a buy signal appears
        if row[f'buy_{coin}'] == 1 and balance > 0:

            if balance < trade_value:
                trade_value = balance # Prevent buying more than possible
            coins_bought = trade_value / price  # Calculate how many coins we can buy
            total_invested += trade_value
            coin_holdings += coins_bought
            balance -= trade_value  # Reduce balance

    # Final value: Cash + value of remaining coins
    final_balance = balance + (coin_holdings * final_price)
    
    if verbose:
        print(f"Initial Capital: ${initial_capital:.2f}")
        print(f"Coin Holdings: {coin_holdings:.8f} BTC")
        print(f"Coin Holdings in dollars: ${coin_holdings*final_price:.2f}")
        print(f"Total Invested: ${total_invested:.2f}")
        print(f"Final Balance: ${final_balance:.2f}")
        print(f"Total Profit/Loss: ${final_balance - initial_capital:.2f}")
        
    return format_output(
        initial_capital= initial_capital, 
        coint_holdings= coin_holdings, 
        final_price = final_price, 
        total_invested = total_invested, 
        final_balance = final_balance
    )


def simulate_model_buyer(
        df: pd.DataFrame, 
        initial_capital: float, 
        trade_value: float, 
        coin: str,
        verbose: bool = True
    ) -> float:

    balance = initial_capital  # Initial money in USD
    coin_holdings = 0  # Number of coins owned
    total_invested = 0  # Total money invested
    final_balance = 0  # Final balance after simulation
    final_price = df[coin].iloc[-1]  # Final price of the coin

    for _, row in df.iterrows():
        price = row[coin]  # Get current coin price

        if balance < 0:
            final_balance = balance + (coin_holdings * final_price)
            total_invested = initial_capital - balance
            if verbose:
                print("No more money to invest!")
                print(f"Initial Capital: ${initial_capital:.2f}")
                print(f"Coin Holdings in BTC: {coin_holdings:.8f}")
                print(f"Coin Holdings in dollars: ${coin_holdings*final_price:.2f}")            
                print(f"Total Invested: ${total_invested:.2f}")
                print(f"Final Balance: ${final_balance:.2f}")
            return format_output(
                initial_capital= initial_capital, 
                coint_holdings= coin_holdings, 
                final_price = final_price, 
                total_invested = total_invested, 
                final_balance = final_balance
            )

        # Buy logic: Buy $10 worth of the coin when a buy signal appears
        if row[f'buy_{coin}'] == 1 and balance > 0:

            if balance < trade_value:
                trade_value = balance # Prevent buying more than possible
            coins_bought = trade_value / price  # Calculate how many coins we can buy
            total_invested += trade_value
            coin_holdings += coins_bought
            balance -= trade_value  # Reduce balance

    # Final value: Cash + value of remaining coins
    final_balance = balance + (coin_holdings * final_price)
    
    if verbose:
        print(f"Initial Capital: ${initial_capital:.2f}")
        print(f"Coin Holdings: {coin_holdings:.8f} BTC")
        print(f"Coin Holdings in dollars: ${coin_holdings*final_price:.2f}")
        print(f"Total Invested: ${total_invested:.2f}")
        print(f"Final Balance: ${final_balance:.2f}")
        print(f"Total Profit/Loss: ${final_balance - initial_capital:.2f}")
        
    return format_output(
        initial_capital= initial_capital, 
        coint_holdings= coin_holdings, 
        final_price = final_price, 
        total_invested = total_invested, 
        final_balance = final_balance
    )


def simulate_dca(
        df:pd.DataFrame,
        coin: str,
        initial_capital:float, 
        trade_value:float, 
        investment_interval:str,
        verbose:bool = True
    ) -> float:

    balance = initial_capital  # Initial money in USD
    coin_holdings = 0  # Number of coins owned
    total_invested = 0 # Total money invested on DCA
    final_balance = 0  # Final balance after simulation
    final_price = df[coin].iloc[-1]  # Final price of the coin
    btc_bought = 0 # Number of BTC bought

    # Normalize days to "YYYY-MM-DD" format
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Define days to buy based on investment interval
    dca_dates = pd.date_range(
        start=df['date'].min(), 
        end=df['date'].max(), 
        freq=investment_interval
    ).normalize()

    for date in dca_dates:
        # Converts date to "YYYY-MM-DD" format
        date = date.date()
        price = df.loc[df['date'] == date, coin].values[0]

        if balance < 0:
            final_balance = balance + (coin_holdings * final_price)
            if verbose:
                print('Stop!')
                print(f"Initial Capital: ${initial_capital:.2f}")
                print(f"Coin Holdings: {coin_holdings:.8f} BTC")
                print(f"Coin Holdings in dolars: ${coin_holdings*final_price:.2f}")
                print(f"Total Invested: ${total_invested:.2f}")
                print(f"Final Balance: ${final_balance:.2f}")
                print(f"Total Profit/Loss: ${final_balance - initial_capital:.2f}")
            return format_output(
                initial_capital= initial_capital, 
                coint_holdings= coin_holdings, 
                final_price = final_price, 
                total_invested = total_invested, 
                final_balance = final_balance
            )

        if date in df['date'].values:
            btc_bought = trade_value / price
            coin_holdings += btc_bought
            total_invested += trade_value
            balance -= trade_value

    final_balance = balance + (coin_holdings * final_price)
    if verbose:
        print(f"Initial Capital: ${initial_capital:.2f}")
        print(f"Coin Holdings: {coin_holdings:.8f} BTC")
        print(f"Coin Holdings in dolars: ${coin_holdings*final_price:.2f}")
        print(f"Total Invested: ${total_invested:.2f}")
        print(f"Final Balance: ${final_balance:.2f}")    
        print(f"Total Profit/Loss: ${final_balance - initial_capital:.2f}")
    return format_output(
        initial_capital= initial_capital, 
        coint_holdings= coin_holdings, 
        final_price = final_price, 
        total_invested = total_invested, 
        final_balance = final_balance
    )


def roi(invested_amount: float, final_balance: float) -> float:
    """
    Calculates the return over investment done.
    ---------
    Parameters
    ----------
    - inital_capital (float): Capital available for investment.
    - final_balance (float): Final balance after simulation.
    ----------
    Returns
    ---------
    - ROI (float): Return over the investment in percentage.
    """
    return ((final_balance - invested_amount) / invested_amount) * 100