from data_loader import DataLoader

data_loader = DataLoader()

data_loader.load_from_json(file_name = 'input.json')

data_loader.load_from_db()

initial_inventories = data_loader.get_initial_inventories()

forbidden_inventories = data_loader.get_forbidden_inventories()

traveling_inventories = data_loader.get_traveling_inventories()

fc_by_sku_meli = data_loader.get_fc_by_sku_meli()

typings = data_loader.get_typings()

forecasts = data_loader.get_forecasts()

days_on_hand = data_loader.get_days_on_hand()

conservation_factor = data_loader.get_conservation_factor()

sku_meli_list = data_loader.get_sku_meli_list()

''' Output '''
traveling_inventory = {}  # dictionary <(skuMeli, FC, FC, week): valor>

week = data_loader.get_week_a_optimizar()

for sku_meli in sku_meli_list:

	# print((sku_meli, 'SAO1', week))

	# calculo el stock disponible en San Pablo
	available_stock_SAO_1 = initial_inventories[(sku_meli, 'SAO1', week)]
	if (sku_meli, 'SAO1', week) in forbidden_inventories.keys():
		available_stock_SAO_1 -= forbidden_inventories[(sku_meli, 'SAO1', week)]

	available_stock_SAO_2 = initial_inventories[(sku_meli, 'SAO2', week)]
	if (sku_meli, 'SAO2', week) in forbidden_inventories.keys():
		available_stock_SAO_2 -= forbidden_inventories[(sku_meli, 'SAO2', week)]

	available_stock_SAO = available_stock_SAO_1 + available_stock_SAO_2

	# calculo el stock disponible en Porto Alegre
	# TODO: hay inventarios inamovibles en POA que tengan que ser tenidos en cuenta?
	available_stock_POA = initial_inventories[(sku_meli, 'POA', week)]
	if (sku_meli, 'PAO', week) in traveling_inventories.keys():
		available_stock_POA += traveling_inventories[(sku_meli, 'POA', week)]

	typing = typings[sku_meli]

	'''		
	if available_stock_POA < forecasts[(sku_meli, 'POA', week)]:
			print("estoy jugado, tengo que pedir")
	else:
			print("todo tranca")
	'''

	'''
	# me fijo si se trata un sku_meli con política reorder point
	typing_SAO = typings[(sku_meli, 'SAO')]
	typing_POA = typings[(sku_meli, 'POA')]

	punto_de_reorden_POA = puntos_de_reorden[(sku_meli, 'POA')]

	inventario_final_deseado_SAO = 0
	
	if (typing_POA == '' and typing_SAO == ''):
		pass
	elif (typing_POA == '' and typing_SAO == ''):
		pass
	else:
		pass
	'''

	cantidad_a_transferir = min(0, 1)

	'''Spliteo SAO1 y SAO2'''
	fc_sao_seller = fc_by_sku_meli[sku_meli]

	if fc_sao_seller == 'SAO1':
		fc_sao_other = 'SAO2'
	else:
		fc_sao_other = 'SAO1'

	transf_fc_sao_seller = 0
	transf_fc_sao_other = 0

	if cantidad_a_transferir <= initial_inventories[(sku_meli, fc_sao_other, week)]:
		transf_fc_sao_other = cantidad_a_transferir
		transf_fc_sao_seller = 0
	else:
		transf_fc_sao_other = initial_inventories[(sku_meli, fc_sao_seller, week)]
		transf_fc_sao_seller = cantidad_a_transferir - transf_fc_sao_other

	traveling_inventories.update({(sku_meli, fc_sao_seller, 'POA', week): transf_fc_sao_seller})
	traveling_inventories.update({(sku_meli, fc_sao_other, 'POA', week): transf_fc_sao_other})

	final_sao_seller = initial_inventories[(sku_meli, fc_sao_seller, week)] \
					   - transf_fc_sao_seller
	final_sao_other = initial_inventories[(sku_meli, fc_sao_other, week)] \
					  - transf_fc_sao_other
	final_fc_poa = initial_inventories[(sku_meli, 'POA', week)] \
				   + transf_fc_sao_seller + transf_fc_sao_other

	initial_inventories.update({(sku_meli, fc_sao_seller, week + 1): final_sao_seller})
	initial_inventories.update({(sku_meli, fc_sao_other, week + 1): final_sao_other})
	initial_inventories.update({(sku_meli, 'POA', week + 1): final_fc_poa})
