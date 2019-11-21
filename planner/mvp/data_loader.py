import json
import datetime
from dao import Dao


class DataLoader:
	def __init__(self):

		self.date_format = '%Y-%m-%d %H:%M:%S'
		self.initial_inventories = {}  # dictionary <(skuMeli, FC) : float>
		self.forbidden_inventories = {}  # dictionary <(skuMeli, FC) : float>
		self.traveling_inventories = {}  # dictionary <(skuMeli, FC, week) : float> (arriving)
		self.fc_by_sku_meli = {}  # dictionary <skuMeli : FC>

		self.typings = {}  # dictionary <skuMeli : typing>
		self.forecasts = {}  # dictionary <(skuMeli, FC, week) : float>
		self.weekly_averages = {}  # dictionary <(skuMeli, FC, week) : float>

		self.safety_stock_days_on_hand = {}  # dictionary <(skuMeli, FC, week) : float>
		self.origin_preference_factor = 0  # float between 0 and 1

		self.sku_meli_list = []  # list <skuMeli>
		self.review_period = 7
		self.optimized_week = None

	def load_from_json(self, file_name):

		with open('{}'.format(file_name)) as json_file:
			data = json.load(json_file)

		for item in data["initial_inventories"]:
			self.initial_inventories.update(
				{(item["sku_meli"], item["fc"]): item["value"]})

		for item in data["forbidden_inventories"]:
			self.initial_inventories.update({(item["sku_meli"], item["fc"]): item["value"]})

		for item in data["traveling_inventories"]:
			week = datetime.datetime.strptime(item["week"], self.date_format)
			self.initial_inventories.update({(item["sku_meli"], item["fc"], week): item["value"]})

		for item in data["fc_by_sku_meli"]:
			self.fc_by_sku_meli.update({item["sku_meli"]: item["fc"]})

		for item in data["typings"]:
			self.typings.update({item["sku_meli"]: item["value"]})

		for item in data["forecasts"]:
			week = datetime.datetime.strptime(item["week"], self.date_format)
			self.forecasts.update({(item["sku_meli"], item["fc"], week): item["value"]})

		for item in data["safety_stock_days_on_hand"]:
			self.safety_stock_days_on_hand.update(
				{(item["sku_meli"], item["fc"]): item["value"]})

		for item in data["parameters"]["sku_meli_list"]:
			self.sku_meli_list.append(item["sku_meli"])

		self.optimized_week = data["parameters"]["optimized_week"]

		self.origin_preference_factor = data["parameters"]["origin_preference_factor"]

	def load_from_db(self):

		with open('{}'.format('config.json')) as json_file:
			config = json.load(json_file)

		dao = Dao(db = config["db"], host = config["host"], port = config["port"],
				  user = config["user"], password = config["password"], schema = config["schema"])

		# TODO: complete method in order to fill the dictionaries from tables in database

	def load_from_csv(self):

		# TODO: complete method in order to fill the dictionaries from csv files
		pass

	def get_initial_inventory(self, sku_meli, fc):

		if (sku_meli, fc) in self.initial_inventories.keys():
			return self.initial_inventories[(sku_meli, fc)]
		else:
			return 0

	def get_forbidden_inventory(self, sku_meli, fc):
		if (sku_meli, fc) in self.forbidden_inventories.keys():
			return self.forbidden_inventories[(sku_meli, fc)]
		else:
			return 0

	def get_traveling_inventory(self, sku_meli, fc):
		if (sku_meli, fc) in self.traveling_inventories.keys():
			return self.traveling_inventories[(sku_meli, fc)]
		else:
			return 0

	def get_fc_by_sku_meli(self, sku_meli):
		if sku_meli in self.fc_by_sku_meli.keys():
			return self.fc_by_sku_meli[sku_meli]
		else:
			return 'SAO1'

	def get_typing(self, sku_meli):
		if sku_meli in self.typings.keys():
			return self.typings[sku_meli]
		else:
			return 'NO FORECASTEABLE'

	def get_forecast(self, sku_meli, fc, week):
		if (sku_meli, fc, week) in self.forecasts.keys():
			return self.forecasts[(sku_meli, fc, week)]
		else:
			return 0

	def get_safety_stock_days_on_hand(self, sku_meli, fc):
		if (sku_meli, fc) in self.safety_stock_days_on_hand.keys():
			return self.safety_stock_days_on_hand[(sku_meli, fc)]
		else:
			return 0

	def get_origin_preference_factor(self):
		return self.origin_preference_factor

	def get_sku_meli_list(self):
		return self.sku_meli_list

	def get_optimized_week(self):
		return datetime.datetime.strptime(self.optimized_week, '%Y-%m-%d %H:%M:%S')
