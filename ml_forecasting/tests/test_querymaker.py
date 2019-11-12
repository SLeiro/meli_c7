from datetime import datetime
from ml_forecasting.etl.base import TEMPLATE_BUYS, QueryMaker


def test_date_to_querymaker_one_query():
    date_from = datetime.strptime('2019-08-01', '%Y-%m-%d')
    date_to = datetime.strptime('2019-08-03', '%Y-%m-%d')
    delta = 7
    site = 'MLB'

    queries = QueryMaker(date_from, date_to, delta, site, TEMPLATE_BUYS).queries()

    TEST_TEMPLATE = TEMPLATE_BUYS.format('MLB', '2019-08-01', '2019-08-04')

    assert len(queries) == 1
    assert TEST_TEMPLATE == queries[0][1]


def test_date_to_querymaker_more_than_one_query():
    date_from = datetime.strptime('2019-08-01', '%Y-%m-%d')
    date_to = datetime.strptime('2019-08-10', '%Y-%m-%d')
    delta = 7
    site = 'MLB'

    queries = QueryMaker(date_from, date_to, delta, site, TEMPLATE_BUYS).queries()

    TEST_TEMPLATE_1 = TEMPLATE_BUYS.format('MLB', '2019-08-01', '2019-08-08')
    TEST_TEMPLATE_2 = TEMPLATE_BUYS.format('MLB', '2019-08-08', '2019-08-11')

    assert len(queries) == 2
    assert TEST_TEMPLATE_1 == queries[0][1]
    assert TEST_TEMPLATE_2 == queries[1][1]


def test_train_zipcode_template_querymaker():
    date_from = datetime.strptime('2019-08-01', '%Y-%m-%d')
    date_to = datetime.strptime('2019-08-14', '%Y-%m-%d')
    delta = 7
    site = 'MLB'

    queries = QueryMaker(date_from, date_to, delta, site, TEMPLATE_BUYS).queries()

    TEST_TEMPLATE_1 = TEMPLATE_BUYS.format('MLB', '2019-08-01', '2019-08-08')
    TEST_TEMPLATE_2 = TEMPLATE_BUYS.format('MLB', '2019-08-08', '2019-08-15')

    assert len(queries) == 2

    assert site in queries[0][0]
    assert site in queries[1][0]

    assert TEST_TEMPLATE_1 == queries[0][1]
    assert TEST_TEMPLATE_2 == queries[1][1]
