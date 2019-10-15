import numpy as np


# Define Default configs
DEFAULT_DTYPES = {
    'ORD_ORDER_ID': np.float,
    'ITE_ITEM_ID': np.float,
    'TIM_DAY_WINNING_DATE': np.object,
    'TIM_TIME_WINNING_DATE': np.int,
    'BID_QUANTITY_OK': np.int,
    'SHP_SHIPMENT_ID': np.object,
    'CUS_CUST_ID_SEL': np.int,
    'CUS_CUST_ID_BUY': np.int,
    'CAT_CATEG_ID': np.int,
    'ITE_CATALOG_PRODUCT_ID_STR': np.object,
    'DOM_DOMAIN_ID': np.object,
    'BID_BASE_CURRENT_PRICE': np.float,
    'BID_CURRENT_PRICE': np.float,
    'ITE_BASE_CURRENT_PRICE': np.float,
    'ITE_SITE_CURRENT_PRICE': np.float,
    'SHP_SPEED': np.object,
    'SHP_SPEED_OFFSET': np.object,
    'SHP_PICKING_TYPE_ID': np.object,
    'SHP_REAL_COST': np.object,
    'SHP_REAL_COST_USD': np.object,
    'SHP_SEND_COST': np.object,
    'SHP_RULE_COST': np.object,
    'SHP_CARRIER_COST_CALCULATED': np.object,
    'order_item_title': np.object,
    'ITE_ATT_ATTRIBUTE_ID': np.object,
    'ite_att_value_name': np.object,

    'sender_shp_add_city_id': np.object,
    'sender_shp_add_state_id': np.object,
    'sender_shp_add_zip_code': np.object,
    'receiver_shp_add_city_id': np.object,
    'receiver_shp_add_state_id': np.object,
    'receiver_shp_add_zip_code': np.object,
}


PARSE_DATES = [
    'TIM_DAY_WINNING_DATE',
]


INTEREST_COLS =  [
    'ORD_ORDER_ID',
    'ITE_ITEM_ID',
    'TIM_DAY_WINNING_DATE',
    'TIM_TIME_WINNING_DATE',
    'BID_QUANTITY_OK',
    'SHP_SHIPMENT_ID',
    'receiver_shp_add_city_id',
    'receiver_shp_add_state_id',
    'receiver_shp_add_zip_code',
]


# Group configs by site
CONFIGS_BY_SITE = {
    'MLB': {
        'DTYPES': DEFAULT_DTYPES,
        'PARSE_DATES': PARSE_DATES,
        'INTEREST_COLS': INTEREST_COLS,
    },
}


def required_cols(config_dict):
    required_cols = config_dict['INTEREST_COLS'].copy()
    return required_cols


def train_dtypes(config_dict):
    defaults = config_dict['DTYPES']
    return {k: defaults.get(k) for k in required_cols(config_dict)}
