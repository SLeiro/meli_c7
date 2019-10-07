from datetime import datetime
from ml_forecasting.etl.base import TEMPLATE_SHIPPING, QueryMaker


def test_date_to_querymaker_one_query():
    date_from = datetime.strptime('2019-08-01', '%Y-%m-%d')
    date_to = datetime.strptime('2019-08-03', '%Y-%m-%d')
    delta = 7
    site = 'MLB'

    queries = QueryMaker(date_from, date_to, delta, site, TEMPLATE_SHIPPING).queries()

    TEST_TEMPLATE = TEMPLATE_SHIPPING.format('MLB', '2019-08-01 00:00:00', '2019-08-04 00:00:00')

    assert len(queries) == 1
    assert TEST_TEMPLATE == queries[0][1]


def test_date_to_querymaker_more_than_one_query():
    date_from = datetime.strptime('2019-08-01', '%Y-%m-%d')
    date_to = datetime.strptime('2019-08-10', '%Y-%m-%d')
    delta = 7
    site = 'MLB'

    queries = QueryMaker(date_from, date_to, delta, site, TEMPLATE_SHIPPING).queries()

    TEST_TEMPLATE_1 = TEMPLATE_SHIPPING.format('MLB', '2019-08-01 00:00:00', '2019-08-08 00:00:00')
    TEST_TEMPLATE_2 = TEMPLATE_SHIPPING.format('MLB', '2019-08-08 00:00:00', '2019-08-11 00:00:00')

    assert len(queries) == 2
    assert TEST_TEMPLATE_1 == queries[0][1]
    assert TEST_TEMPLATE_2 == queries[1][1]


def test_train_zipcode_template_querymaker():
    date_from = datetime.strptime('2019-08-01', '%Y-%m-%d')
    date_to = datetime.strptime('2019-08-14', '%Y-%m-%d')
    delta = 7
    site = 'MLB'

    queries = QueryMaker(date_from, date_to, delta, site, TEMPLATE_SHIPPING).queries()

    TEST_TEMPLATE_1 = TEMPLATE_SHIPPING.format('MLB', '2019-08-01 00:00:00', '2019-08-08 00:00:00')
    TEST_TEMPLATE_2 = TEMPLATE_SHIPPING.format('MLB', '2019-08-08 00:00:00', '2019-08-15 00:00:00')

    assert len(queries) == 2

    assert site in queries[0][0]
    assert site in queries[1][0]

    assert TEST_TEMPLATE_1 == queries[0][1]
    assert TEST_TEMPLATE_2 == queries[1][1]
