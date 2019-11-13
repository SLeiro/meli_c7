import pandas as pd
import sqlalchemy


class Dao:
	"""
	Data Access Object Class used to retreive and write data to postgres databases
	"""

	def __init__(self, host, port, user, password, db, schema = 'public'):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.db = db
		self.schema = schema
		self.engine = sqlalchemy.create_engine(self.get_connection_string())

	def get_connection_string(self):
		return 'postgresql+psycopg2://{}:{}@{}:{}/{}'. \
			format(self.user, self.password, self.host, self.port, self.db)

	def get_engine(self):
		return self.engine

	def run_query(self, query):
		with self.engine.connect() as conn:
			if self.schema != 'public':
				conn.execute(
					"SET search_path TO {}, public".format(self.schema))
			conn.execute(query)

	def download_from_query(self, query):
		with self.engine.connect() as conn:
			if self.schema != 'public':
				conn.execute("SET search_path TO {}, public".format(self.schema))
			return pd.read_sql(query, conn)

	def upload_from_dataframe(self, df, table_name, if_exists = 'replace', chunksize = 1000000):
		df.to_sql(table_name, self.engine, schema = self.schema,
				  if_exists = if_exists, index = False, chunksize = chunksize)
