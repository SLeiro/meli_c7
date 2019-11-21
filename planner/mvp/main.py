from planner import Planner
from data_loader import DataLoader


def main():
	data_loader = DataLoader()
	data_loader.load_from_json(file_name = 'input.json')

	planner = Planner(data_loader = data_loader)

	planner.execute_planning()

	print('\nOptimized Transfers:')
	for key, value in planner.optimized_transfers.items():
		print(key, value)


if __name__ == '__main__':
	main()
