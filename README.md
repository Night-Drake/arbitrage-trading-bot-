This Python script automates triangular arbitrage on the KuCoin exchange using the CCXT library. It detects profitable trading loops and executes trades in real-time.

🚀 Features:

  ✅ Fetches real-time bid/ask prices from KuCoin

  ✅ Detects arbitrage opportunities across 3-coin combinations

  ✅ Calculates net profit after fees

  ✅ Executes trades automatically when profitable (via limit orders)

  ✅ Waits for each order to be fully completed before proceeding

  ✅ Logs profitable trades to a file

📂 File Structure:

  api.env – Stores your KuCoin API credentials (API_KEY, API_SECRET, API_PASSPHRASE)
  
  arbitrage cobinations.txt – List of coin combinations in the format:
  
  COIN1/USDT -> COIN2/COIN1 -> COIN2/USDT

  profitable_combinations.txt – Output log of profitable trades detected

⚙️ How It Works:

  Loads environment variables and initializes KuCoin API

  Reads arbitrage paths from file

  Checks real-time prices for each combination

  Runs arbitrage simulation using triangular_arbitrage()

  If profitable:

    Executes real trades in order: Buy → Trade → Sell

  Waits for each order to complete

  Logs all profitable opportunities to a file

💸 Fee Assumption:

  The script assumes a 0.1% trading fee per transaction. Adjustable via the fee variable.

📌 Requirements:

  Python 3.7+
  
  ccxt
  
  python-dotenv


