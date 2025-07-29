import os
from dotenv import load_dotenv
import ccxt
import time

load_dotenv('api.env')

apiKey = os.getenv('API_KEY')
apiSecret = os.getenv('API_SECRET')
apiPassphrase = os.getenv('API_PASSPHRASE')

ku = ccxt.kucoin({
    'enableRateLimit': True,
    'apiKey': apiKey,
    'secret': apiSecret,
    'password': apiPassphrase,
})

def wait_for_order_completion(exchange, order_id):
    while True:
        order = exchange.fetch_order(order_id)
        if order['status'] == 'closed':
            print(f"Order {order_id} has been completed.")
            break
        elif order['status'] == 'canceled':
            print(f"Order {order_id} has been canceled.")
            break
        elif order['status'] == 'failed':
            print(f"Order {order_id} has failed.")
            break
        time.sleep(0.5)

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
    return None, None


def extract_before_slash(phrase):
    # Split the phrase using '/' as the delimiter
    parts = phrase.split('/')
    
    # Take the part before the first '/'
    result = parts[0]
    
    return result
def extract_after_slash(phrase):
    # Split the phrase using '/' as the delimiter
    parts = phrase.split('/')
    
    # Take the part before the first '/'
    result = parts[1]
    
    return result

def coin_balance(coin):
    try:
        trading_balance = ku.fetch_balance(params={'type': 'trade'})
        # Check if 'USDT' key exists in the response
        if 'USDT' in trading_balance:
            usdt_balance = trading_balance[coin]['free']
        else:
            print("No USDT balance information found in the response.")
            return None
    except Exception as e:
        print(f"Error fetching trading balance: {e}")
        return None
    return usdt_balance

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

def execution_for_normal(coin1, price1, coin2, price2, coin3, price3, available_usdt, ku):
    try:
        available_usdt=1
        # Define the fee rate
        fee_rate = 0.001  # 0.1%

        order_amount_coin1 = available_usdt / price1
        order_amount_coin2 = order_amount_coin1 / price2
        order_amount_coin3 = order_amount_coin2 / price3

        order_amount_coin1 *= (1 - fee_rate)
        order_amount_coin2 *= (1 - fee_rate)
        order_amount_coin3 *= (1 - fee_rate)

        # Create limit buy order for the first coin
        order_buy_coin1 = ku.create_limit_buy_order(coin1, order_amount_coin1, price1)
        print(f"Placed limit buy order for {order_amount_coin1} {coin1} at price {price1}")

        # Wait for the buy order to be filled
        wait_for_order_completion(ku, order_buy_coin1['id'])
        print(f"Placed limit buy order completed")

        # Create limit sell order for the second coin
        order_sell_coin2 = ku.create_limit_sell_order(coin2, order_amount_coin2, price2)
        print(f"Placed limit sell order for {order_amount_coin2} {coin2} at price {price2}")

        # Wait for the sell order to be filled
        wait_for_order_completion(ku, order_sell_coin2['id'])
        print(f"Placed limit sell order completed")

        # Create limit sell order for the third coin
        order_sell_coin3 = ku.create_limit_sell_order(coin3, order_amount_coin3, price3)
        print(f"Placed limit sell order for {order_amount_coin3} {coin3} at price {price3}")

        # Wait for the sell order to be filled
        wait_for_order_completion(ku, order_sell_coin3['id'])
        print(f"Placed limit sell order completed")

    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def arb_logic(arbitrage_combinations, available_usdt, fee, exchange, output_profitable):
    for combination in arbitrage_combinations:
        symbol_to_check1, symbol_to_check2, symbol_to_check3 = combination.split(" -> ")

        coin3_bid, coin3_ask = get_kucoin_price(exchange, symbol_to_check3) 
        coin2_bid, coin2_ask  = get_kucoin_price(exchange, symbol_to_check2)
        coin1_bid, coin1_ask = get_kucoin_price(exchange, symbol_to_check1)

        # Skip the iteration if any of the prices are not available
        if any(price is None for price in [coin1_bid, coin1_ask, coin3_bid, coin3_ask, coin2_bid, coin2_ask]):
            print(f"Skipping combination due to missing prices: {combination}")
            continue

        triangle = triangular_arbitrage(coin1_ask, coin2_ask, coin3_bid, available_usdt, fee)

        if triangle > 0:
            with open(output_profitable, "a") as file:
                file.write(f"with normale Profitable Combination: {combination}, Profit: ${triangle:.2f}\n")
                print(f"Profitable Combination: {combination}, Profit\n")
            execution_for_normal(symbol_to_check3, coin3_ask, symbol_to_check2, coin2_bid, symbol_to_check1, coin1_bid, available_usdt, ku)
        else:   
            print(f"Loss Combination: {combination}, loss")

exchange = ccxt.kucoin()                        #exchange we are using
available_usdt = coin_balance('USDT')                #get the amount of usdt we have
fee = 0.1 / 100                                 #fee per transaction
with open('arbitrage cobinations.txt', 'r') as file:                           #reads the file with the combinations
    arbitrage_combinations = [line.strip() for line in file.readlines()]

output_profitable = 'profitable_combinations.txt'           #file with the profit numbers and combinations     
    
arb_logic(arbitrage_combinations, available_usdt, fee, exchange, output_profitable)