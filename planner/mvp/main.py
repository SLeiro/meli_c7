from planner import Planner
from data_loader import DataLoader


def main():
	data_loader = DataLoader()
	data_loader.load_from_json(file_name = 'input.json')

	planner = Planner(data_loader = data_loader)

	planner.execute_planning()

	print('\nOptimized Transfers: {}'.format(planner.optimized_transfers))


if __name__ == '__main__':
	main()
