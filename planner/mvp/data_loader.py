import json


class DataLoader:
	def __init__(self, file_name):
		with open('{}'.format(file_name)) as json_file:
			self.data = json.load(json_file)

		self.inventarios_iniciales = {}  # dictionary <(skuMeli, FC, semana): valor>
		self.inventarios_inamovibles = {}  # dictionary <(skuMeli, FC): valor>
		self.inventarios_en_transito = {}  # dictionary <(skuMeli, FC, semana): valor> (llegada)
		self.fc_por_sku_meli = {}  # dictionary <skuMeli: FC>
		self.tipificaciones = {}  # dictionary <(skuMeli, FC): tipo >
		self.forecasts = {}  # dictionary <(skuMeli, FC, semana): valor>
		self.coberturas = {}  # dictionary <(skuMeli, FC, semana): valor>
		self.puntos_de_reorden = {}  # dictionary <(skuMeli, FC, semana): valor>
		self.listado_sku_meli = []  # list <skuMeli>
		self.listado_semanas = []  # list <semanas>
		self.factor_consevador = 0

		for item in self.data["inventarios_iniciales"]:
			self.inventarios_iniciales.update(
				{(item["sku_meli"], item["fc"], item["semana"]): item["valor"]})

		for item in self.data["inventarios_inamovibles"]:
			self.inventarios_inamovibles.update({(item["sku_meli"], item["fc"]): item[
				"valor"]})

		for item in self.data["inventarios_en_transito"]:
			self.inventarios_en_transito.update(
				{(item["sku_meli"], item["fc"], item["semana"]): item["valor"]})

		for item in self.data["fc_por_sku_meli"]:
			self.fc_por_sku_meli.update({item["sku_meli"]: item["fc"]})

		for item in self.data["tipificaciones"]:
			self.tipificaciones.update({(item["sku_meli"], item["fc"]): item["valor"]})

		for item in self.data["forecasts"]:
			self.forecasts.update({(item["sku_meli"], item["fc"], item["semana"]): item["valor"]})

		for item in self.data["coberturas"]:
			self.coberturas.update({(item["sku_meli"], item["fc"], item["semana"]): item["valor"]})

		for item in self.data["puntos_de_reorden"]:
			self.puntos_de_reorden.update(
				{(item["sku_meli"], item["fc"]): item["punto_de_reorden"]})

		for item in self.data["listado_sku_meli"]:
			self.listado_sku_meli.append(item["sku_meli"])

		for item in self.data["listado_semanas"]:
			self.listado_semanas.append(item["semana"])

		self.factor_consevador = self.data["factor_conservador"]

	def get_inventarios_iniciales(self):

		return self.inventarios_iniciales

	def get_inventarios_inamovibles(self):

		return self.inventarios_inamovibles

	def get_inventarios_en_transito(self):

		return self.inventarios_en_transito

	def get_fc_por_sku_meli(self):

		return self.fc_por_sku_meli

	def get_tipificaciones(self):

		return self.tipificaciones

	def get_forecasts(self):

		return self.forecasts

	def get_coberturas(self):

		return self.coberturas

	def get_puntos_de_reorden(self):

		return self.puntos_de_reorden

	def get_factor_consevacion(self):
		return self.factor_consevador

	def get_listado_sku_meli(self):

		return self.listado_sku_meli

	def get_listado_semanas(self):

		return self.listado_semanas
