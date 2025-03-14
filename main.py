import requests
import pandas as pd
import numpy as np
import talib
import time

# === Telegram Credentials ===
TELEGRAM_BOT_TOKEN = "8031378823:AAEFHr6_GfC5X5PNNbBW6LyioNGgxO5zKUI"
CHAT_ID = "5849543153"

# === CoinMarketCap API Credentials ===
CMC_API_KEY = "7e1bbe1a-aa17-47f0-aaba-dd90b5d3f8b4"

# === Fetch Crypto Data from CoinMarketCap ===
def fetch_crypto_data(symbol="BTC"):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"symbol": symbol, "convert": "USD"}
    response = requests.get(url, headers=headers, params=params).json()
    
    price = response["data"][symbol]["quote"]["USD"]["price"]
    return price

# === Send Messages to Telegram ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, params=params)

# === Technical Analysis (SMC + ICT) ===
def analyze_market(symbol="BTC"):
    prices = []
    
    # Simulating price history (Replace with real data if available)
    for _ in range(100):
        prices.append(fetch_crypto_data(symbol))
        time.sleep(1)  # Avoid API Rate Limits
    
    df = pd.DataFrame(prices, columns=["close"])
    
    # Indicators
    df["RSI"] = talib.RSI(df["close"], timeperiod=14)
    df["MACD"], df["MACD_Signal"], _ = talib.MACD(df["close"])
    df["Upper_BB"], df["Middle_BB"], df["Lower_BB"] = talib.BBANDS(df["close"])
    df["SMA_50"] = talib.SMA(df["close"], timeperiod=50)
    df["SMA_200"] = talib.SMA(df["close"], timeperiod=200)
    
    # Market Structure Analysis
    df["Higher_High"] = df["close"] > df["close"].shift(1)
    df["Lower_Low"] = df["close"] < df["close"].shift(1)
    
    # Smart Money Concepts (SMC)
    df["Order_Block"] = np.where(df["Higher_High"] & df["Lower_Low"], "OB", "N/A")
    df["Fair_Value_Gap"] = np.where((df["Higher_High"]) & (df["RSI"] > 70), "FVG", "N/A")
    
    # Generate Trade Signal
    latest = df.iloc[-1]
    trade_signal = "HOLD"
    entry_price, stop_loss, take_profit = latest["close"], None, None

    if latest["RSI"] < 30 and latest["MACD"] > latest["MACD_Signal"]:
        trade_signal = "BUY"
        stop_loss = entry_price * 0.98
        take_profit = entry_price * 1.05

    elif latest["RSI"] > 70 and latest["MACD"] < latest["MACD_Signal"]:
        trade_signal = "SELL"
        stop_loss = entry_price * 1.02
        take_profit = entry_price * 0.95

    # Send Signal
    message = f"""
    🔹 Crypto Trading Bot Alert 🔹
    📊 {symbol}/USD
    💰 Price: {latest['close']} USD
    📈 RSI: {latest['RSI']:.2f}
    📉 MACD: {latest['MACD']:.2f}, Signal: {latest['MACD_Signal']:.2f}
    🎯 Trade Signal: {trade_signal}
    📍 Entry: {entry_price} USD
    🔻 Stop Loss: {stop_loss} USD
    🚀 Take Profit: {take_profit} USD
    🔵 Order Block: {latest['Order_Block']}
    🟢 Fair Value Gap: {latest['Fair_Value_Gap']}
    """
    send_telegram_message(message)

# === Run the Bot Every Minute ===
while True:
    analyze_market("BTC")
    time.sleep(60)
