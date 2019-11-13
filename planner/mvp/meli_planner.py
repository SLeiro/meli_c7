from data_loader import DataLoader

data_loader = DataLoader()

data_loader.load_from_json(file_name = 'input.json')

data_loader.load_from_db()

initial_stocks = data_loader.get_inventarios_iniciales()

forbidden_stocks = data_loader.get_inventarios_inamovibles()

in_transit_stocks = data_loader.get_inventarios_en_transito()

fc_por_sku_meli = data_loader.get_fc_por_sku_meli()

tipificaciones = data_loader.get_tipificaciones()

forecasts = data_loader.get_forecasts()

days_on_hand = data_loader.get_coberturas()

factor_consevacion = data_loader.get_factor_consevacion()

listado_sku_meli = data_loader.get_listado_sku_meli()

''' Output '''
transferencias = {}  # dictionary <(skuMeli, FC, FC, semana): valor>

semana = data_loader.get_semana_a_optimizar()

for sku_meli in listado_sku_meli:

	# print((sku_meli, 'SAO1', semana))

	# calculo el stock disponible en San Pablo
	available_stock_SAO_1 = inventarios_iniciales[(sku_meli, 'SAO1', semana)]
	if (sku_meli, 'SAO1', semana) in inventarios_inamovibles.keys():
		stock_disponible_SAO_1 -= inventarios_inamovibles[(sku_meli, 'SAO1', semana)]

	available_stock_SAO_2 = inventarios_iniciales[(sku_meli, 'SAO2', semana)]
	if (sku_meli, 'SAO2', semana) in inventarios_inamovibles.keys():
		stock_disponible_SAO_2 -= inventarios_inamovibles[(sku_meli, 'SAO2', semana)]

	stock_disponible_SAO = stock_disponible_SAO_1 + stock_disponible_SAO_2

	# calculo el stock disponible en Porto Alegre
	# TODO: hay inventarios inamovibles en POA que tengan que ser tenidos en cuenta?
	stock_disponible_POA = inventarios_iniciales[(sku_meli, 'POA', semana)]
	if (sku_meli, 'PAO', semana) in inventarios_en_transito.keys():
		stock_disponible_POA += inventarios_en_transito[(sku_meli, 'POA', semana)]

	tipificacion = tipificaciones[sku_meli]

	'''		
	if stock_disponible_POA < forecasts[(sku_meli, 'POA', semana)]:
			print("estoy jugado, tengo que pedir")
	else:
			print("todo tranca")
	'''

	'''
	# me fijo si se trata un sku_meli con política reorder point
	tipificacion_SAO = tipificaciones[(sku_meli, 'SAO')]
	tipificacion_POA = tipificaciones[(sku_meli, 'POA')]

	punto_de_reorden_POA = puntos_de_reorden[(sku_meli, 'POA')]

	inventario_final_deseado_SAO = 0
	
	if (tipificacion_POA == '' and tipificacion_SAO == ''):
		pass
	elif (tipificacion_POA == '' and tipificacion_SAO == ''):
		pass
	else:
		pass
	'''

	cantidad_a_transferir = min(0, 1)

	'''Spliteo SAO1 y SAO2'''
	fc_sao_seller = fc_por_sku_meli[sku_meli]

	if fc_sao_seller == 'SAO1':
		fc_sao_other = 'SAO2'
	else:
		fc_sao_other = 'SAO1'

	transf_fc_sao_seller = 0
	transf_fc_sao_other = 0

	if cantidad_a_transferir <= inventarios_iniciales[(sku_meli, fc_sao_other, semana)]:
		transf_fc_sao_other = cantidad_a_transferir
		transf_fc_sao_seller = 0
	else:
		transf_fc_sao_other = inventarios_iniciales[(sku_meli, fc_sao_seller, semana)]
		transf_fc_sao_seller = cantidad_a_transferir - transf_fc_sao_other

	transferencias.update({(sku_meli, fc_sao_seller, 'POA', semana): transf_fc_sao_seller})
	transferencias.update({(sku_meli, fc_sao_other, 'POA', semana): transf_fc_sao_other})

	final_sao_seller = inventarios_iniciales[(sku_meli, fc_sao_seller, semana)] \
					   - transf_fc_sao_seller
	final_sao_other = inventarios_iniciales[(sku_meli, fc_sao_other, semana)] \
					  - transf_fc_sao_other
	final_fc_poa = inventarios_iniciales[(sku_meli, 'POA', semana)] \
				   + transf_fc_sao_seller + transf_fc_sao_other

	inventarios_iniciales.update({(sku_meli, fc_sao_seller, semana + 1): final_sao_seller})
	inventarios_iniciales.update({(sku_meli, fc_sao_other, semana + 1): final_sao_other})
	inventarios_iniciales.update({(sku_meli, 'POA', semana + 1): final_fc_poa})
