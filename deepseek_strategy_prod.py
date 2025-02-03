import yfinance as yf
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os  # Import os to read environment variables
import smtplib
from email.mime.text import MIMEText
import os

# Function to send email notification
def send_email(subject, message):
    sender_email = os.getenv("EMAIL_SENDER")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    app_password = os.getenv("EMAIL_APP_PASSWORD")  # Store email password as an env variable

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

# 🔹 Load API keys from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = 'https://api.alpaca.markets' #'https://api.alpaca.markets'  # paper: 'https://paper-api.alpaca.markets'

if not API_KEY or not API_SECRET:
    raise ValueError("❌ Missing Alpaca API credentials. Ensure ALPACA_API_KEY and ALPACA_SECRET_KEY are set.")

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

# 🔹 Trade settings
symbol = "UPST"
quantity = 15
start_date = "2022-01-01"
end_date = "2024-12-31"

# 🔹 Fetch historical data from Yahoo Finance
barset = yf.download(symbol, start=start_date, end=end_date)

# 🔹 Calculate moving averages and generate signals
barset["50_MA"] = barset["Close"].rolling(window=50).mean()
barset["200_MA"] = barset["Close"].rolling(window=200).mean()
barset["Signal"] = 0
barset.iloc[50:, barset.columns.get_loc("Signal")] = np.where(
    barset["50_MA"].iloc[50:] > barset["200_MA"].iloc[50:], 1, -1
)
barset["Position"] = barset["Signal"].diff()

# 🔹 Backtest the strategy
barset["Market_Return"] = barset["Close"].pct_change()
barset["Strategy_Return"] = barset["Market_Return"] * barset["Signal"].shift(1)
barset["Cumulative_Market_Return"] = (1 + barset["Market_Return"]).cumprod()
barset["Cumulative_Strategy_Return"] = (1 + barset["Strategy_Return"]).cumprod()

# 🔹 Plot results
plt.figure(figsize=(14, 7))
plt.plot(barset.index, barset["Cumulative_Market_Return"], label="Market Return")
plt.plot(barset.index, barset["Cumulative_Strategy_Return"], label="Strategy Return")
plt.legend()
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.title(f"Trading Strategy Performance for {symbol}")
plt.show()

# 🔹 Check current position (avoid duplicate trades)
try:
    position = api.get_position(symbol)
    has_position = True
except:
    has_position = False  # No active position

# 🔹 Implement the strategy (Live Trading)
latest_signal = barset["Position"].iloc[-1]

print(f"Latest signal: {latest_signal}")
print(f"Has position: {has_position}")

if latest_signal == 1 and not has_position:
    print(f"✅ Buying {quantity} shares of {symbol}...")
    api.submit_order(
        symbol=symbol,
        qty=quantity,
        side="buy",
        type="market",
        time_in_force="gtc"
    )
    send_email(f"🚀 {symbol} Buy Alert", f"Bought {quantity} shares of {symbol}")
elif latest_signal == -1 and has_position:
    print(f"✅ Selling {quantity} shares of {symbol}...")
    api.submit_order(
        symbol=symbol,
        qty=quantity,
        side="sell",
        type="market",
        time_in_force="gtc"
    )
    send_email(f"🚀 {symbol} Sell Alert", f"Sold {quantity} shares of {symbol}")
else:
    print("🔹 No trade executed.")