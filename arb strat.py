# Initialize values
btc_usd = 40000
eth_btc = 0.05
eth_usd = 2000
initial_usd = 2
initial_btc = 0.00008 
fee = 0.1 / 100  # Convert percentage to decimal

def triangular_arbitrage(btc_usd_bid, eth_usd_ask, eth_btc_bid, initial_usd, fee):
    # Buy ETH with USD (use ask price for buying)
    eth_buy = initial_usd / eth_usd_ask

    # Apply transaction fee for buying Ethereum
    eth_buy_after_fee = eth_buy * (1 - fee)

    # Buy BTC with ETH (use bid price for buying)
    btc_buy = eth_buy_after_fee * eth_btc_bid

    # Apply transaction fee for buying Bitcoin
    btc_buy_after_fee = btc_buy * (1 - fee)

    # Sell BTC for USD (use bid price for selling)
    btc_sell_usd = btc_buy_after_fee * btc_usd_bid

    # Apply transaction fee for selling Bitcoin
    btc_sell_usd_after_fee = btc_sell_usd * (1 - fee)

    # Calculate profit
    profit = btc_sell_usd_after_fee - initial_usd

    return profit

def reverse_triangular_arbitrage(btc_usd_bid, eth_btc_ask, eth_usd_bid, initial_usd, fee):
    # Buy BTC with USD (use bid price for buying)
    btc_buy = initial_usd / btc_usd_bid

    # Apply transaction fee for buying BTC
    btc_buy_after_fee = btc_buy * (1 - fee)

    # Sell ETH for BTC (use ask price for selling)
    eth_sell_btc = btc_buy_after_fee / eth_btc_ask

    # Apply transaction fee for selling ETH
    eth_sell_btc_after_fee = eth_sell_btc * (1 - fee)

    # Sell USD for ETH (use bid price for selling)
    usd_sell_eth = eth_sell_btc_after_fee * eth_usd_bid

    # Apply transaction fee for selling USD
    usd_sell_eth_after_fee = usd_sell_eth * (1 - fee)

    # Calculate profit
    profit = usd_sell_eth_after_fee - initial_usd

    return profit


pro=triangular_arbitrage(btc_usd, eth_usd, eth_btc, initial_usd, fee)
print(pro)

prof = reverse_triangular_arbitrage(btc_usd, eth_btc, eth_usd, initial_usd, fee)

print(prof)

