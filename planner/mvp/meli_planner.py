from data_loader import DataLoader
from dateutil.relativedelta import relativedelta

data_loader = DataLoader()
data_loader.load_from_json(file_name = 'input.json')
# data_loader.load_from_db()

forbidden_inventories = data_loader.get_forbidden_inventories()
traveling_inventories = data_loader.get_traveling_inventories()
fc_by_sku_meli = data_loader.get_fc_by_sku_meli()
typings = data_loader.get_typings()
forecasts = data_loader.get_forecasts()
days_on_hand = data_loader.get_days_on_hand()
objective_inventories = data_loader.get_objective_inventories()
origin_preference_factor = data_loader.get_origin_preference_factor()
sku_meli_list = data_loader.get_sku_meli_list()

''' Output '''
optimized_transfers = {}  # dictionary <(skuMeli, FC, FC): valor>

week_1 = data_loader.get_optimized_week()
week_2 = data_loader.get_optimized_week() + relativedelta(weeks = 1)
week_3 = data_loader.get_optimized_week() + relativedelta(weeks = 2)

for sku_meli in sku_meli_list:

	# Available stock in SAO
	# print(initial_inventories)
	available_stock_SAO_1 = data_loader.get_initial_inventories(sku_meli, 'SAO1')
	if (sku_meli, 'SAO1', week_1) in forbidden_inventories.keys():
		available_stock_SAO_1 -= forbidden_inventories[(sku_meli, 'SAO1')]

	available_stock_SAO_2 = data_loader.get_initial_inventories(sku_meli, 'SAO2')
	if (sku_meli, 'SAO2', week_1) in forbidden_inventories.keys():
		available_stock_SAO_2 -= forbidden_inventories[(sku_meli, 'SAO2')]

	available_stock_SAO = available_stock_SAO_1 + available_stock_SAO_2

	# Available stock in POA
	# TODO: is there any forbidden inventory in POA that we should be taking into account?
	available_stock_POA = data_loader.get_initial_inventories(sku_meli, 'POA')
	if (sku_meli, 'PAO', week_1) in traveling_inventories.keys():
		available_stock_POA += traveling_inventories[(sku_meli, 'POA')]

	forecast_next_2_weeks_SAO = forecasts[(sku_meli, 'SAO', week_1)] + \
								forecasts[(sku_meli, 'SAO', week_2)]
	forecast_next_2_weeks_POA = forecasts[(sku_meli, 'POA', week_1)] + \
								forecasts[(sku_meli, 'SAO', week_2)]

	print('available SAO: {}. available POA: {}'.format(available_stock_SAO, available_stock_POA))
	print('fcst 2 weeks SAO: {}. fcst 2 weeks POA: {}'.format(forecast_next_2_weeks_SAO,
															  forecast_next_2_weeks_POA))

	typing = typings[sku_meli]

	objective_stock_POA = 0
	objective_stock_SAO = 0

	if typing == 'FA ALTO':
		objective_stock_POA = objective_inventories[(sku_meli, 'POA')]
		objective_stock_SAO = objective_inventories[(sku_meli, 'SAO')]
	elif typing == 'FA BAJO':
		objective_stock_POA = 0
		objective_stock_SAO = 0
	else:
		objective_stock_POA = 0
		objective_stock_SAO = 0

	if available_stock_SAO >= objective_stock_SAO + forecast_next_2_weeks_SAO:
		print("caso optimista")
		w3_forecast_SAO = forecasts[(sku_meli, 'SAO', week_3)]
		w3_forecast_POA = forecasts[(sku_meli, 'POA', week_3)]

		optimized_transfer = ((w3_forecast_POA / w3_forecast_SAO) *
							  (available_stock_SAO - forecast_next_2_weeks_SAO)
							  - available_stock_POA + forecast_next_2_weeks_POA) / \
							 (1 + w3_forecast_POA / w3_forecast_SAO)

		print('optimized transfer before bounds : {}'.format(optimized_transfer))
		# We check if the transfer quantity calculated doesn't break stocks in either SAO or POA
		min_required_transfer = objective_stock_POA - (
				available_stock_POA - forecast_next_2_weeks_POA)
		max_required_transfer = - objective_stock_SAO + (
				available_stock_SAO - forecast_next_2_weeks_SAO)

		print('min bound: {}. max bound: {}'.format(min_required_transfer, max_required_transfer))

		optimized_transfer = max(optimized_transfer, min_required_transfer)
		optimized_transfer = min(optimized_transfer, max_required_transfer)

		print('optimized transfer post bounds : {}'.format(optimized_transfer))

	else:
		optimized_transfer = 0  # TODO: pending business definition

	'''SAO1 and SAO2 splitting'''
	fc_sao_seller = fc_by_sku_meli[sku_meli]

	if fc_sao_seller == 'SAO1':
		fc_sao_other = 'SAO2'
	else:
		fc_sao_other = 'SAO1'

	transf_fc_sao_seller = 0
	transf_fc_sao_other = 0

	if optimized_transfer <= data_loader.get_initial_inventories(sku_meli, fc_sao_other):
		transfer_fc_sao_other = optimized_transfer
		transfer_fc_sao_seller = 0
	else:
		transfer_fc_sao_other = data_loader.get_initial_inventories(sku_meli, fc_sao_seller)
		transfer_fc_sao_seller = optimized_transfer - transfer_fc_sao_other

	optimized_transfers.update({(sku_meli, fc_sao_seller, 'POA'): transfer_fc_sao_seller})
	optimized_transfers.update({(sku_meli, fc_sao_other, 'POA'): transfer_fc_sao_other})

print(optimized_transfers)
