from dateutil.relativedelta import relativedelta


class Planner:

	def __init__(self, data_loader):
		self.data_loader = data_loader
		self.optimized_transfers = {}  # dictionary <(skuMeli, FC, FC): valor>

	def get_objective_inventory(self, sku_meli, fc, week_2):

		typing = self.data_loader.get_typing(sku_meli)

		if typing == 'FA ALTO':
			objective_inventory = self.data_loader.get_forecast(sku_meli, fc, week_2)
			objective_inventory += (1.0 / 7.0) \
								   * self.data_loader.get_forecast(sku_meli, fc, week_2) \
								   * self.data_loader.get_safety_stock_days_on_hand(sku_meli, fc)
		else:
			# TODO: change input for average, max or other statistical of historical weekly sales
			objective_inventory = self.data_loader.get_forecast(sku_meli, fc, week_2)
			objective_inventory += (1.0 / 7.0) \
								   * self.data_loader.get_forecast(sku_meli, fc, week_2) \
								   * self.data_loader.get_safety_stock_days_on_hand(sku_meli, fc)

		return objective_inventory

	def generate_transfer(self, sku_meli, week_1, week_2):
		# Available stock in SAO
		available_SAO_1 = self.data_loader.get_initial_inventory(sku_meli, 'SAO1')
		available_SAO_1 -= self.data_loader.get_forbidden_inventory(sku_meli, 'SAO1')

		available_SAO_2 = self.data_loader.get_initial_inventory(sku_meli, 'SAO2')
		available_SAO_2 -= self.data_loader.get_forbidden_inventory(sku_meli, 'SAO2')

		available_SAO = available_SAO_1 + available_SAO_2

		# Available stock in POA
		# TODO: is there any forbidden inventory in POA that we should be taking into account?
		available_POA = self.data_loader.get_initial_inventory(sku_meli, 'POA')
		available_POA += self.data_loader.get_traveling_inventory(sku_meli, 'POA')

		forecast_week_1_SAO = self.data_loader.get_forecast(sku_meli, 'SAO', week_1)
		forecast_week_1_POA = self.data_loader.get_forecast(sku_meli, 'POA', week_1)

		# Objective stocks in SAO and POA
		objective_SAO = self.get_objective_inventory(sku_meli, 'SAO', week_2)
		objective_POA = self.get_objective_inventory(sku_meli, 'POA', week_2)

		print('sku_meli: {}'.format(sku_meli))
		print('\tavailable: SAO: {}, POA: {}'.format(available_SAO, available_POA))
		print('\tfcst week_1: SAO: {}, POA: {}'.format(forecast_week_1_SAO, forecast_week_1_POA))
		print('\tobjective: SAO: {}, POA: {}'.format(objective_SAO, objective_POA))

		if available_SAO >= objective_SAO + forecast_week_1_SAO and available_SAO + available_POA \
				>= objective_SAO + objective_POA + forecast_week_1_SAO + forecast_week_1_POA:

			print('\tOverall: Surplus.')
			forecast_week_2_SAO = self.data_loader.get_forecast(sku_meli, 'SAO', week_2)
			forecast_week_2_POA = self.data_loader.get_forecast(sku_meli, 'POA', week_2)

			optimized_transfer = ((forecast_week_2_POA / forecast_week_2_SAO) *
								  (available_SAO - forecast_week_1_SAO)
								  - available_POA + forecast_week_1_POA) / \
								 (1 + forecast_week_2_POA / forecast_week_2_SAO)

			print('\toptimized transfer before bounds : {}'.format(optimized_transfer))

			# Check if the optimized transfer quantity doesn't break stocks in SAO or POA
			min_required_transfer = objective_POA - (available_POA - forecast_week_1_POA)
			max_required_transfer = - objective_SAO + (available_SAO - forecast_week_1_SAO)

			print('\tmin : {}. max : {}'.format(min_required_transfer, max_required_transfer))

			optimized_transfer = max(optimized_transfer, min_required_transfer)
			optimized_transfer = min(optimized_transfer, max_required_transfer)

			print('\toptimized transfer post bounds : {}'.format(optimized_transfer))

		elif available_SAO >= objective_SAO + forecast_week_1_SAO:
			print('\tOverall: Shortage. SAO: Surplus')
			optimized_transfer = - objective_SAO + (available_SAO - forecast_week_1_SAO)
			print('\toptimized transfer: {}'.format(optimized_transfer))

		else:
			print('\tOverall: Shortage. SAO: Shortage')
			optimized_transfer = 0
			print('\toptimized transfer: {}'.format(optimized_transfer))

		return optimized_transfer

	def split_and_save_transfers(self, sku_meli, optimized_transfer):
		fc_sao_seller = self.data_loader.get_fc_by_sku_meli(sku_meli)

		if fc_sao_seller == 'SAO1':
			fc_sao_other = 'SAO2'
		else:
			fc_sao_other = 'SAO1'

		if optimized_transfer <= self.data_loader.get_initial_inventory(sku_meli, fc_sao_other):
			transfer_fc_sao_other = optimized_transfer
			transfer_fc_sao_seller = 0
		else:
			transfer_fc_sao_other = self.data_loader.get_initial_inventory(sku_meli, fc_sao_seller)
			transfer_fc_sao_seller = optimized_transfer - transfer_fc_sao_other

		self.optimized_transfers.update(
			{(sku_meli, fc_sao_seller, 'POA'): transfer_fc_sao_seller})
		self.optimized_transfers.update(
			{(sku_meli, fc_sao_other, 'POA'): transfer_fc_sao_other})

	def execute_planning(self):

		week_1 = self.data_loader.get_optimized_week()
		week_2 = self.data_loader.get_optimized_week() + relativedelta(weeks = 1)

		for sku_meli in self.data_loader.get_sku_meli_list():
			optimized_transfer = self.generate_transfer(sku_meli, week_1, week_2)
			self.split_and_save_transfers(sku_meli, optimized_transfer)
