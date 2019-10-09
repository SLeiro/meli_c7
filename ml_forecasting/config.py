import numpy as np


# Define Default configs
DEFAULT_DTYPES = {
    'ORD_ORDER_ID': np.float,
    'ITE_ITEM_ID': np.float,
    'TIM_DAY_WINNING_DATE': np.object,
    'TIM_TIME_WINNING_DATE': np.int,
    'BID_QUANTITY_OK': np.int,
    'SHP_SHIPMENT_ID': np.object,

    'receiver_shp_add_city_id': np.object,
    'receiver_shp_add_state_id': np.object,
    'receiver_shp_add_zip_code': np.object,
    
    'TIM_DAY_WINNING_DATE': np.object,
}


DEFAULT_PARSE_DATES = [
    'TIM_DAY_WINNING_DATE',
]


INTEREST_COLS =  [
    'ord_order_id',
    'ite_item_id',
    'tim_day_winning_date',
    'tim_time_winning_date',
    'bid_quantity_ok',
    'shp_shipment_id',
    'receiver_shp_add_city_id',
    'receiver_shp_add_state_id',
    'receiver_shp_add_zip_code',
]

# Group configs by site
CONFIGS_BY_SITE = {
    'MLB': {
        'DTYPES': DEFAULT_DTYPES,
        'PARSE_DATES': DEFAULT_PARSE_DATES,
        'INTEREST_COLS': INTEREST_COLS,
    },
}


def required_cols(config_dict):
    required_cols = config_dict['INTEREST_COLS'].copy()
    return required_cols
