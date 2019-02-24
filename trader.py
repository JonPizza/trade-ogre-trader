'''
THIS IS A CRYPTOCURRENCY TRADING BOT

USE AT YOUR OWN RISK, AS YOU HAVE A GOOD CHANCE OF LOOSING MONEY

BTC TIPS: 3QGG4dJbbNhmJSkoAUFDF5VvHZ7sJ7zZ5z

LTC TIPS: LNZGxrFtdaF6GKjnFBPegPbex9jrN1h4SQ

RVN TIPS (KAAAAAW): RGT5QK9jwurbFZJCAqrF281cQSjU9LQhDV
'''

binance_api_key = 'YOURKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

binance_secret_key = 'YOURSECRETXXXXXXXXXXXXXXXXXXXXXXXXXX'

trade_ogre_api_key = 'YOURKEYXXXXXXXXXXXXXXXXXXXX'

trade_ogre_secret_key = 'YOURSECETXXXXXXXXXXXXXXXXXXXXXXX'

btc_fed = 0.007

risk = 0.0001




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




class Binance:

	def __init__(self, binance_api, binance_secret):
		self.binance_api = binance_api
		self.binance_secret = binance_secret

	def get_market_info(self):
		'''
		LTC data at [1]
		'''
		api_response = requests.get('https://api.binance.com/api/v1/ticker/24hr')
		return json.loads(api_response.content.decode('utf-8'))

'''

Create classes with API keys.

'''

binance = Binance(binance_api_key, binance_secret_key)
trade_ogre = TradeOgre(trade_ogre_api_key, trade_ogre_secret_key)


bulk_trade_data = [['0', 'INDEXFILLER' , 1], ['1', 'INDEXFILLER', 0]]
trade_counter = 0

prev_buy = 0
prev_sell = 1


def show_bal():
	x = trade_ogre.get_bal('BTC')
	y = trade_ogre.get_bal('LTC')

	print(f'[^] Your BTC balance is {x}, the starting amount was {base_btc_bal}.')
	print(f'[^] Your LTC balance is {y}, the starting amount was {base_bal_ltc}.')





def update_ave():
	binance_day_hi = float(binance.get_market_info()[1]['highPrice'])
	trade_ogre_day_hi = float(trade_ogre.get_market_info()[30]['BTC-LTC']['high'])

	ave_hi = (binance_day_hi+trade_ogre_day_hi)/2

	binance_day_low = float(binance.get_market_info()[1]['lowPrice'])
	trade_ogre_day_low = float(trade_ogre.get_market_info()[30]['BTC-LTC']['low'])

	ave_low = (binance_day_low+trade_ogre_day_low)/2
	return (ave_low, ave_hi)



def check_profit(buy_price, sell_price):
	print(f'[.] Possible Profit: {sell_price - buy_price}')
	
	if (sell_price - buy_price) <= min_profit_per_trade:
		return False
	else:
		return True




def evan_slave_buy_low(total=1):
	'''
	Total needs to be at least 1, it works like total * min purchace amount
	'''
	global trade_counter, bulk_trade_data, prev_buy

	min_buy_amount = 0.00005
	day_low = update_ave()[0]

	#FIND MIN AMOUNT NEEDED TO BUY AT MIN PRICE
	while True:
		if (day_low * min_buy_amount) > (btc_fed/2.15)*total:
			day_low_risk = day_low + risk

			bulk_trade_data.append([str(trade_counter), 'INDEXFILLER', min_buy_amount])
			prev_buy = day_low_risk

			if check_profit(prev_buy, prev_sell) == True:
				trade_data = trade_ogre.buy_ltc(round(min_buy_amount, 6), round(day_low_risk, 6))

				trade_counter += 1
				break
			else:
				print('Unprofitable Trade Averted Captian!')
				break

		else:
			min_buy_amount += 0.00005





def evan_slave_sell_high(total=1):
	'''
	Total needs to be at least 1, it works like total * min purchace amount
	'''
	global trade_counter, bulk_trade_data, prev_sell


	min_sell_amount = 0.0005
	day_hi = update_ave()[1]


	#FIND MIN AMOUNT NEEDED TO BUY AT SPECIFIED PRICE PRICE
	while True:
		if (day_hi * min_sell_amount) > (btc_fed/2.15)*total:
			day_hi_risk = day_hi - risk


			bulk_trade_data.append([str(trade_counter), 'INDEXFILLER', min_sell_amount])
			prev_sell = day_hi_risk

			if check_profit(prev_buy, prev_sell) == True:
				trade_ogre.sell_ltc(round(min_sell_amount, 6), round(day_hi_risk, 6))

				trade_counter += 1
				break
			else:
				print('Unprofitable Trade Averted Captian!')
				break

		else:
			min_sell_amount += 0.0001




num = 0
def evan_slave_cancel(uuid):
	global bulk_trade_data, trade_counter, num

	trade_ogre.cancel_order(uuid)

	if num != 0:
		bulk_trade_data = []
		trade_counter = 0
	else:
		num = 1

	



if __name__ == '__main__':
	base_btc_bal = trade_ogre.get_bal('BTC')
	base_bal_ltc = trade_ogre.get_bal('LTC')

	print(f'[^] Your BTC balance is {base_btc_bal}.')
	print(f'[^] Your LTC balance is {base_bal_ltc}.')

	minutes = 0



	while True:
		print('\n')
		evan_slave_cancel('all')
		print('\n')

		evan_slave_buy_low()
		print('\n')

		evan_slave_sell_high()
		print('\n')

		print(f"[^] Your BTC balance is {trade_ogre.get_bal('BTC')}, change of {float(trade_ogre.get_bal('BTC'))-float(base_btc_bal)} (If no '-' it is positive)")
		print(f"[^] Your LTC balance is {trade_ogre.get_bal('LTC')}, change of {float(trade_ogre.get_bal('LTC'))-float(base_bal_ltc)} (If no '-' it is positive)")
		print(f"[:] It's been {minutes} minute(s).")
		print('\n')




		time.sleep(30)
		minutes += 0.5
	


