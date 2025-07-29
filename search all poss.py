import ccxt

def get_kucoin_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        if ticker is not None and 'bid' in ticker and 'ask' in ticker:
            return ticker['bid'], ticker['ask']
        else:
            print(f"Invalid ticker data for symbol: {symbol}")
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Return a default value or handle the error as needed
    return None, None

def triangular_arbitrage(coin3_ask, coin2_ask, coin1_bid, initial_usd, fee):
    # Buy ETH with USD (use ask price for buying)
    eth_buy = initial_usd / coin1_bid

    # Apply transaction fee for buying Ethereum
    eth_buy_after_fee = eth_buy * (1 - fee)

    # Buy BTC with ETH (use bid price for buying)
    btc_buy = eth_buy_after_fee * coin2_ask

    # Apply transaction fee for buying Bitcoin
    btc_buy_after_fee = btc_buy * (1 - fee)

    # Sell BTC for USD (use bid price for selling)
    btc_sell_usd = btc_buy_after_fee * coin3_ask

    # Apply transaction fee for selling Bitcoin
    btc_sell_usd_after_fee = btc_sell_usd * (1 - fee)

    # Calculate profit
    profit = btc_sell_usd_after_fee - initial_usd

    return profit


def reverse_triangular_arbitrage(coin3_bid, coin2_ask, coin1_bid, initial_usd, fee):
    # Buy BTC with USD (use bid price for buying)
    btc_buy = initial_usd / coin3_bid

    # Apply transaction fee for buying BTC
    btc_buy_after_fee = btc_buy * (1 - fee)

    # Sell ETH for BTC (use ask price for selling)
    eth_sell_btc = btc_buy_after_fee / coin2_ask

    # Apply transaction fee for selling ETH
    eth_sell_btc_after_fee = eth_sell_btc * (1 - fee)

    # Sell USD for ETH (use bid price for selling)
    usd_sell_eth = eth_sell_btc_after_fee * coin1_bid

    # Apply transaction fee for selling USD
    usd_sell_eth_after_fee = usd_sell_eth * (1 - fee)

    # Calculate profit
    profit = usd_sell_eth_after_fee - initial_usd

    return profit

def arb_logic(arbitrage_combinations, output_profitable, output_loss):
    income = 0
    for combination in arbitrage_combinations:
        symbol_to_check1, symbol_to_check2, symbol_to_check3 = combination.split(" -> ")

        eth_usd_bid, eth_usd_ask = get_kucoin_price(exchange, symbol_to_check3) 
        eth_btc_bid, eth_btc_ask  = get_kucoin_price(exchange, symbol_to_check2)
        btc_usd_bid, btc_usd_ask = get_kucoin_price(exchange, symbol_to_check1)

        # Skip the iteration if any of the prices are not available
        if any(price is None for price in [btc_usd_bid, btc_usd_ask, eth_usd_bid, eth_usd_ask, eth_btc_bid, eth_btc_ask]):
            print(f"Skipping combination due to missing prices: {combination}")
            with open(output_loss, "a") as file:
                file.write(f"{combination}\n")
            continue

        triangle = triangular_arbitrage(btc_usd_ask, eth_btc_ask, eth_usd_bid, usd_initial, fee)
        reverse_triangle = reverse_triangular_arbitrage(btc_usd_bid, eth_btc_bid, eth_usd_ask, usd_initial, fee)

        if triangle > 0:
            with open(output_profitable, "a") as file:
                file.write(f"with normale Profitable Combination: {combination}, Profit: ${triangle:.2f}\n")
                print(f"Profitable Combination: {combination}, Profit\n")
                income += triangle
        elif reverse_triangle > 0:
            with open(output_profitable, "a") as file:
                file.write(f"with rev Profitable Combination: {combination}, Profit: ${reverse_triangle:.2f}\n")
                print(f"Profitable Combination: {combination}, Profit\n")
                income += reverse_triangle
        else:   
            print(f"Loss Combination: {combination}, loss")
    print(income)

with open('arbitrage cobinations.txt', 'r') as file:
    arbitrage_combinations = [line.strip() for line in file.readlines()]

# Output file names
output_profitable = 'profitable_combinations.txt'
output_loss = 'loss_combinations.txt'

# Create the exchange object
exchange = ccxt.kucoin()

# Set initial values
usd_initial = 1
fee = 0.1 / 100

# Run the arbitrage logic
arb_logic(arbitrage_combinations, output_profitable, output_loss)
