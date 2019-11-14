from dateutil.relativedelta import relativedelta


class Planner:

	def __init__(self, data_loader):
		self.data_loader = data_loader
		self.optimized_transfers = {}  # dictionary <(skuMeli, FC, FC): valor>

	def get_objective_inventory(self, sku_meli, fc):
		typing = self.data_loader.get_typings(sku_meli)

		if typing == 'FA ALTO':
			objective_inventory = self.data_loader.get_objective_inventories(sku_meli, fc)
		elif typing == 'FA BAJO':
			objective_inventory = 0
		else:
			objective_inventory = 0

		return objective_inventory

	def split_and_save_transfers(self, sku_meli, optimized_transfer):
		fc_sao_seller = self.data_loader.get_fc_by_sku_meli(sku_meli)

		if fc_sao_seller == 'SAO1':
			fc_sao_other = 'SAO2'
		else:
			fc_sao_other = 'SAO1'

		if optimized_transfer <= self.data_loader.get_initial_inventories(sku_meli, fc_sao_other):
			transfer_fc_sao_other = optimized_transfer
			transfer_fc_sao_seller = 0
		else:
			transfer_fc_sao_other = self.data_loader.get_initial_inventories(sku_meli,
																			 fc_sao_seller)
			transfer_fc_sao_seller = optimized_transfer - transfer_fc_sao_other

		self.optimized_transfers.update(
			{(sku_meli, fc_sao_seller, 'POA'): transfer_fc_sao_seller})
		self.optimized_transfers.update(
			{(sku_meli, fc_sao_other, 'POA'): transfer_fc_sao_other})

	def execute_planning(self):

		week_1 = self.data_loader.get_optimized_week()
		week_2 = self.data_loader.get_optimized_week() + relativedelta(weeks = 1)

		for sku_meli in self.data_loader.get_sku_meli_list():

			# Available stock in SAO
			available_stock_SAO_1 = self.data_loader.get_initial_inventories(sku_meli, 'SAO1')
			available_stock_SAO_1 -= self.data_loader.get_forbidden_inventories(sku_meli, 'SAO1')

			available_stock_SAO_2 = self.data_loader.get_initial_inventories(sku_meli, 'SAO2')
			available_stock_SAO_2 -= self.data_loader.get_forbidden_inventories(sku_meli, 'SAO2')

			available_stock_SAO = available_stock_SAO_1 + available_stock_SAO_2

			# Available stock in POA
			# TODO: is there any forbidden inventory in POA that we should be taking into account?
			available_stock_POA = self.data_loader.get_initial_inventories(sku_meli, 'POA')
			available_stock_POA += self.data_loader.get_traveling_inventories(sku_meli, 'POA')

			forecast_next_week_SAO = self.data_loader.get_forecasts(sku_meli, 'SAO', week_1)
			forecast_next_week_POA = self.data_loader.get_forecasts(sku_meli, 'POA', week_1)

			print('available stocks: SAO: {}, POA: {}'.format(available_stock_SAO,
															  available_stock_POA))
			print('fcst next week: SAO: {}, POA: {}'.format(forecast_next_week_SAO,
															forecast_next_week_POA))

			objective_stock_SAO = self.get_objective_inventory(sku_meli, 'SAO')
			objective_stock_POA = self.get_objective_inventory(sku_meli, 'POA')

			if available_stock_SAO >= objective_stock_SAO + forecast_next_week_SAO:
				print("caso optimista")
				w2_forecast_SAO = self.data_loader.get_forecasts(sku_meli, 'SAO', week_2)
				w2_forecast_POA = self.data_loader.get_forecasts(sku_meli, 'POA', week_2)

				optimized_transfer = ((w2_forecast_POA / w2_forecast_SAO) *
									  (available_stock_SAO - forecast_next_week_SAO)
									  - available_stock_POA + forecast_next_week_POA) / \
									 (1 + w2_forecast_POA / w2_forecast_SAO)

				print('optimized transfer before bounds : {}'.format(optimized_transfer))

				# We check if the transfer quantity calculated doesn't break stocks in either
				# SAO or POA
				min_required_transfer = objective_stock_POA - (
						available_stock_POA - forecast_next_week_POA)
				max_required_transfer = - objective_stock_SAO + (
						available_stock_SAO - forecast_next_week_SAO)

				print(
					'min bound: {}. max bound: {}'.format(min_required_transfer,
														  max_required_transfer))

				optimized_transfer = max(optimized_transfer, min_required_transfer)
				optimized_transfer = min(optimized_transfer, max_required_transfer)

				print('optimized transfer post bounds : {}'.format(optimized_transfer))

			else:
				optimized_transfer = 0  # TODO: pending business definition

			self.split_and_save_transfers(sku_meli, optimized_transfer)
