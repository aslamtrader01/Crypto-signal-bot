from telegram import Bot
import requests
import pandas as pd
import ta
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "-5257745535"

bot = Bot(token=BOT_TOKEN)

PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT"
]

TIMEFRAME = "5m"

async def send_signal(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={TIMEFRAME}&limit=100"
    data = requests.get(url).json()

    df = pd.DataFrame(data)
    df["high"] = df[2].astype(float)
    df["low"] = df[3].astype(float)
    df["close"] = df[4].astype(float)

    df["ema9"] = ta.trend.ema_indicator(df["close"], window=9)
    df["ema21"] = ta.trend.ema_indicator(df["close"], window=21)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)

    return df

async def scan():
    while True:
        for pair in PAIRS:
            try:
                df = get_data(pair)

                last = df.iloc[-1]

                entry = round(last["close"], 4)

                if last["ema9"] > last["ema21"] and last["rsi"] > 50:

                    sl = round(last["low"], 4)
                    target = round(entry + (entry - sl) * 2, 4)

                    msg = f"""
🟢 BUY SIGNAL

Pair: {pair}
Entry: {entry}
Stop Loss: {sl}
Target: {target}
RSI: {round(last['rsi'],2)}
"""

                    await send_signal(msg)

                elif last["ema9"] < last["ema21"] and last["rsi"] < 50:

                    sl = round(last["high"], 4)
                    target = round(entry - (sl - entry) * 2, 4)

                    msg = f"""
🔴 SELL SIGNAL

Pair: {pair}
Entry: {entry}
Stop Loss: {sl}
Target: {target}
RSI: {round(last['rsi'],2)}
"""

                    await send_signal(msg)

            except Exception as e:
                print(e)

        await asyncio.sleep(300)

asyncio.run(scan())
