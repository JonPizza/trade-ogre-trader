'''
THIS IS A CRYPTOCURRENCY TRADING BOT

USE AT YOUR OWN RISK, AS YOU HAVE A GOOD CHANCE OF LOSING MONEY (Although you can make $ too!)

BTC TIPS: 3QGG4dJbbNhmJSkoAUFDF5VvHZ7sJ7zZ5z

LTC TIPS: LNZGxrFtdaF6GKjnFBPegPbex9jrN1h4SQ

RVN TIPS (KAAAAAW): RGT5QK9jwurbFZJCAqrF281cQSjU9LQhDV
'''

trade_ogre_api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'

trade_ogre_secret_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'

btc_fed = 0.01 #Put in amount of BTC in acct. Round up.

risk = 0.00013




min_profit_per_trade = btc_fed*0.0002

import requests, json, time

base_url = 'https://tradeogre.com/api/v1' # Base URL to add /XXXX to, doesn't return anything
class TradeOgre:

	def __init__(self, trade_ogre_api, trade_ogre_secret):
		self.trade_ogre_secret = trade_ogre_secret
		self.trade_ogre_api = trade_ogre_api

	def get_market_info(self):
		'''
		LTC data at [30]['BTC-LTC']
		'''

		api_response = requests.get(base_url + '/markets', headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.trade_ogre_secret}'})

		if api_response.status_code == 200:
			return json.loads(api_response.content.decode('utf-8'))
		else:
			return None

	def buy_ltc(self, amount, price):
		'''
		Buys LTC

		MIN AMOUNT IN BTC IS 0.0001
		'''
		api_response = requests.post(base_url + '/order/buy', data = {'market':'BTC-LTC', 'quantity':amount, 'price':price}, auth = (self.trade_ogre_api, self.trade_ogre_secret))
		print(f'[!] Buy placed for {amount} LTC at {price} BTC, total of {round(amount*price, 6)} BTC')
		print(f'[i] Server Code {api_response.status_code}')
		return json.loads(api_response.content.decode('utf-8'))


	def sell_ltc(self, amount, price):
		'''
		Sells LTC

		MIN AMOUNT IN BTC IS 0.0001
		'''
		api_response = requests.post(base_url + '/order/sell', data = {'market':'BTC-LTC', 'quantity':amount, 'price':price}, auth = (self.trade_ogre_api, self.trade_ogre_secret))
		print(f'[!] Sell placed for {amount} LTC at {price} BTC, total of {round(amount*price, 6)} BTC')
		print(f'[i] Server Code {api_response.status_code}')
		return json.loads(api_response.content.decode('utf-8'))


	def cancel_order(self, uuid):
		api_response = requests.post(base_url + '/order/cancel', data = {'uuid':uuid}, auth = (self.trade_ogre_api, self.trade_ogre_secret))
		print(f'[!] Order cancelled for {uuid}')
		print(f'[i] Server Code {api_response.status_code}')
		return json.loads(api_response.content.decode('utf-8'))


	def get_bal(self, currency_ticker):
		api_response = requests.get(base_url + '/account/balances', auth = (self.trade_ogre_api, self.trade_ogre_secret))
		return json.loads(api_response.content.decode('utf-8'))['balances'][currency_ticker]

	def get_order(self):
		api_response = requests.post(base_url + '/account/orders', auth = (self.trade_ogre_api, self.trade_ogre_secret))
		data = json.loads(api_response.content.decode('utf-8'))
		prev_orders = [0, 0]
		ctr = 0

		for i in data:
			if prev_orders[0] != 0 and prev_orders[1] != 0:
				break
			elif i['type'] == 'sell':
				prev_orders[1] = i['price']
			elif i['type'] == 'buy':
				prev_orders[0] = i['price']

		return prev_orders





class Binance:

	def get_market_info(self):
		'''
		LTC data at [1]
		'''
		api_response = requests.get('https://api.binance.com/api/v1/ticker/24hr')
		return json.loads(api_response.content.decode('utf-8'))

	def get_order_book(self):
		#/api/v1/depth
		api_response = requests.get('https://api.binance.com/api/v1/depth', params = {'symbol': 'LTCBTC', 'limit':100})
		return json.loads(api_response.content.decode('utf-8'))


'''

Create classes with API keys.

'''

binance = Binance()
trade_ogre = TradeOgre(trade_ogre_api_key, trade_ogre_secret_key)


def show_bal():
	x = trade_ogre.get_bal('BTC')
	y = trade_ogre.get_bal('LTC')

	print(f'[^] Your BTC balance is {x}, the starting amount was {base_btc_bal}.')
	print(f'[^] Your LTC balance is {y}, the starting amount was {base_bal_ltc}.')


def check_profit(buy_price, sell_price):
	print(f'[i] Possible Profit: {sell_price - buy_price}')

	if (sell_price - buy_price) <= min_profit_per_trade:
		return False
	else:
		return True



# ALGO ONE STARTS HERE!___________________________________________________________________________________________________________________

bulk_trade_data = [['0', 'INDEXFILLER' , 1], ['1', 'INDEXFILLER', 0]]
trade_counter = 0

prev_buy = float(trade_ogre.get_order()[0])
prev_sell = float(trade_ogre.get_order()[1])

def update_ave():
	binance_day_hi = float(binance.get_market_info()[1]['highPrice'])
	trade_ogre_day_hi = float(trade_ogre.get_market_info()[30]['BTC-LTC']['high'])

	ave_hi = (binance_day_hi+trade_ogre_day_hi)/2

	binance_day_low = float(binance.get_market_info()[1]['lowPrice'])
	trade_ogre_day_low = float(trade_ogre.get_market_info()[30]['BTC-LTC']['low'])

	ave_low = (binance_day_low+trade_ogre_day_low)/2
	return (ave_low, ave_hi)


def evan_slave_buy_low(total=1):
	'''
	Total needs to be at least 1, it works like total * min purchace amount
	'''
	global trade_counter, bulk_trade_data, prev_buy

	max_buy_amount = float(trade_ogre.get_bal('BTC')) * 80

	day_low = update_ave()[0]

	#FIND MIN AMOUNT NEEDED TO BUY AT MIN PRICE
	day_low_risk = day_low + risk

	bulk_trade_data.append([str(trade_counter), 'INDEXFILLER', max_buy_amount])
	prev_buy = day_low_risk

	if check_profit(prev_buy, prev_sell) == True:
		trade_data = trade_ogre.buy_ltc(round(max_buy_amount, 8), round(day_low_risk, 8))

		trade_counter += 1
	else:
		print('Unprofitable Trade Averted Captian!')


def evan_slave_sell_high(total=1):
	'''
	Total needs to be at least 1, it works like total * min purchace amount
	'''
	global trade_counter, bulk_trade_data, prev_sell

	max_sell_amount = float(trade_ogre.get_bal('LTC')) - 0.00001

	day_hi = update_ave()[1]


	day_hi_risk = day_hi - risk
	bulk_trade_data.append([str(trade_counter), 'INDEXFILLER', max_sell_amount])
	prev_sell = day_hi_risk

	if check_profit(prev_buy, prev_sell) == True:
		trade_data = trade_ogre.sell_ltc(round(max_sell_amount, 8), round(day_hi_risk, 8))

		trade_counter += 1
	else:
		print('Unprofitable Trade Averted Captian!')



num = 0
def evan_slave_cancel_algo_one(uuid):
	global bulk_trade_data, trade_counter, num

	trade_ogre.cancel_order(uuid)

	if num != 0:
		bulk_trade_data = []
		trade_counter = 0
	else:
		num = 1

def algo_one():
	base_btc_bal = trade_ogre.get_bal('BTC')
	base_bal_ltc = trade_ogre.get_bal('LTC')

	print(f'[^] Your BTC balance is {base_btc_bal}.')
	print(f'[^] Your LTC balance is {base_bal_ltc}.')

	minutes = 0


	while True:
		print('\n')
		evan_slave_cancel_algo_one('all')
		print('\n')

		evan_slave_buy_low()
		print('\n')

		evan_slave_sell_high()
		print('\n')

		print(f"[^] Your BTC balance is {trade_ogre.get_bal('BTC')}, change of {float(trade_ogre.get_bal('BTC'))-float(base_btc_bal)} (If no '-' it is positive)")
		print(f"[^] Your LTC balance is {trade_ogre.get_bal('LTC')}, change of {float(trade_ogre.get_bal('LTC'))-float(base_bal_ltc)} (If no '-' it is positive)")
		print(f"[:] It's been {minutes} minute(s).")
		print('_' * 208)


		time.sleep(60)
		minutes += 1

# ALGO ONE END HERE!___________________________________________________________________________________________________________________

'''
BINANCE DEPTH DATA

{'lastUpdateId': 166970061, 'bids': [['0.01171200', '0.17000000', []], ['0.01171100', '6.09000000', []], ['0.01170800', '30.47000000', []],
 ['0.01170700', '38.12000000', []], ['0.01170400', '74.47000000', []]], 

'asks': [['0.01171700', '0.34000000', []], ['0.01172100', '27.04000000', []], ['0.01172200', '68.59000000', []], ['0.01172400', '80.93000000', []], 
['0.01172600', '2.86000000', []]]}
'''

# ALGO TWO START HERE!.................................................................................................................


prev_buy_2 = prev_buy
prev_sell_2 = prev_sell

def evan_slave_sell_with_depth():
	global prev_sell_2

	chart = binance.get_order_book()
	ideal_sell = 0
	for c_data in chart['bids']:
		bid_price = float(c_data[0])
		bid_amount = float(c_data[1])

		bid_total = bid_price * bid_amount
		ideal_sell += bid_total

		if ideal_sell < 1000:
			if check_profit(prev_buy_2, prev_sell_2) == True:
				max_sell_amount = float(trade_ogre.get_bal('LTC')) - 0.00001
				trade_ogre.sell_ltc(round(max_sell_amount, 8), round(bid_price, 8))
				prev_sell_2 = bid_price
				print(bid_price)
				print(prev_sell_2)
				break

			else:
				print(bid_price)
				print(prev_sell_2)
				print('Unprofitable Trade Averted Captian!')
				break


def evan_slave_buy_with_depth():
	global prev_buy_2

	chart = binance.get_order_book()
	ideal_buy = 0
	for c_data in chart['asks']:
		ask_price = float(c_data[0])
		ask_amount = float(c_data[1])

		ask_total = ask_price * ask_amount
		ideal_buy += ask_total

		if ideal_buy < 1000:
			if check_profit(prev_buy_2, prev_sell_2) == True:

				max_buy_amount = float(trade_ogre.get_bal('BTC')) * 80
				trade_ogre.buy_ltc(round(max_buy_amount, 8), round(ask_price, 8))
				prev_buy_2 = ask_price
				print(ask_price)
				print(prev_buy_2)
				break

			else:
				print(ask_price)
				print(prev_buy_2)
				print('Unprofitable Trade Averted Captian!')
				break


def algo_two():
	base_btc_bal = trade_ogre.get_bal('BTC')
	base_bal_ltc = trade_ogre.get_bal('LTC')

	print(f'[^] Your BTC balance is {base_btc_bal}.')
	print(f'[^] Your LTC balance is {base_bal_ltc}.')

	minutes = 0

	while True:
		print('\n')
		trade_ogre.cancel_order('all')
		print('\n')

		evan_slave_sell_with_depth()
		print('\n')

		evan_slave_buy_with_depth()
		print('\n')

		print(f"[^] Your BTC balance is {trade_ogre.get_bal('BTC')}, change of {float(trade_ogre.get_bal('BTC'))-float(base_btc_bal)} (If no '-' it is positive)")
		print(f"[^] Your LTC balance is {trade_ogre.get_bal('LTC')}, change of {float(trade_ogre.get_bal('LTC'))-float(base_bal_ltc)} (If no '-' it is positive)")
		print(f"[:] It's been {minutes} minute(s).")
		print('_' * 208)


		time.sleep(20)
		minutes += 50





if __name__ == '__main__':
	while True:
		choose_algo = input('Which algorithm do you want to use? Algo 1 is most popular. [1/2] ')
		if choose_algo == '1':
			algo_one()
		elif choose_algo == '2':
			algo_two()
		else:
			print('Only use 1 or 2.')
