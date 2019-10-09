# -*- coding: utf-8 -*-
import logging
import subprocess
import pathlib

from datetime import timedelta

logger = logging.getLogger(__name__)

TEMPLATE_BUYS = """
SELECT
    /* BT_BIDS */
    bids.ord_order_id,
    bids.ite_item_id,
    bids.tim_day_winning_date,
    bids.tim_time_winning_date,
    bids.bid_quantity_ok,
    bids.shp_shipment_id,
    /* JOIN BT_SHP_SHIPMENTS AND LK_SHP_ADDRESS */
    shp.receiver_shp_add_city_id,
    shp.receiver_shp_add_state_id,
    shp.receiver_shp_add_zip_code
FROM WHOWNER.BT_BIDS AS bids
LEFT JOIN (
    SELECT
        /* BT_SHP_SHIPMENTS */
        s.shp_shipment_id,
        /* LK_SHP_ADDRESS */
        add_r.shp_add_city_id AS receiver_shp_add_city_id,
        add_r.shp_add_state_id AS receiver_shp_add_state_id,
        add_r.shp_add_zip_code AS receiver_shp_add_zip_code
    FROM WHOWNER.BT_SHP_SHIPMENTS AS s
    LEFT JOIN whowner.lk_shp_address AS add_r ON
        (s.shp_receiver_address = add_r.shp_add_id)
    ) AS shp
ON (bids.shp_shipment_id = shp.shp_shipment_id)
WHERE bids.sit_site_id = '{}' 
    AND bids.tim_day_winning_date >= '{}'
    AND bids.tim_day_winning_date < '{}'
    AND bids.photo_id ='TODATE';
"""


class QueryMaker:

    def __init__(self, date_from, date_to, delta, site, template):
        # This will download data from date_start to date_stop day by day into a csv
        self.date_start = date_from
        self.date_stop = date_to
        self.date_delta = timedelta(days=delta)
        self.project = 'ST'
        self.site = site
        self.template = template

    def _get_sql_query_template(self):
        return self.template

    def queries(self):
        """
        This method must return a list of tuples. Each tuple must contain a
        filename and a sql query to download. For example:

        [
            ("some_file_1", "select * from some_table;"),
            ("some_file_2" "select * from some_table;"),
        ]
        """
        def _get_current_end(current_end):
            """
            This funcition checks if the current end is at max equal to self.date_to
            in order to avoid downloading data outside of the defined dates.
            """
            if current_end > self.date_stop:
                # Return date_stop plus one day since the query is looking for
                # data strictly smaller than
                return self.date_stop + timedelta(days=1)
            return current_end

        queries = []

        # Initialize the current dates
        current_start = self.date_start
        current_end = _get_current_end(current_start + self.date_delta)

        while current_start < self.date_stop:
            filename = current_start.strftime(self.project + "_" + self.site + "_%Y%m%d.csv")
            date_from = current_start.strftime("%Y-%m-%d %H:%M:%S")
            date_to = current_end.strftime("%Y-%m-%d %H:%M:%S")

            # Get the sql template query
            query_template = self._get_sql_query_template()

            current_query = query_template.format(self.site, date_from, date_to)

            queries.append((filename, current_query))

            # Update the current dates
            current_start = current_end
            current_end = _get_current_end(current_start + self.date_delta)

        return queries


class FastExportNotFound(Exception):
    pass


class FastExportException(Exception):
    pass


class DataDirNotFound(Exception):
    pass


class DataSource:

    def __init__(self, user, password, data_dir_root, site):
        self.user = user
        self.password = password
        self.site = site

        p = pathlib.Path(data_dir_root)

        if not p.exists():
            raise DataDirNotFound(
                "{data_dir_root} is not a directory.".format(data_dir_root=data_dir_root))

        self.data_dir_root = p

    def _complete(self, data_dir):
        _marker = data_dir.joinpath('.datasource')
        _marker.touch()

    def _is_complete(self, data_dir):
        _marker = data_dir.joinpath('.datasource')
        if _marker.exists():
            return True
        return False

    def _data_dir(self, since, until):
        data_dir = self.data_dir_root.joinpath(
            '{type}-{site}-{since:%Y%m%d}-{until:%Y%m%d}'.format(
                type=self.__class__.__name__.lower(), site=self.site, since=since, until=until))

        if not data_dir.exists():
            data_dir.mkdir()

        return data_dir

    def _csvunloader(self, datadir, query, filename, ldap=False):
        """Creates the argument for subprocess.run to call csvunloader.jar and query teradata
        """

        home_folder = pathlib.Path('/')
        csvunloader_path = home_folder.joinpath('fastexport', 'csvunloader.jar')

        if not csvunloader_path.exists():
            raise FastExportNotFound(
                '{csvunloader_path} not found.'.format(csvunloader_path=csvunloader_path))

        _cmd = ['java', '-jar',  str(csvunloader_path),
                '-sql', query,
                '-out',  str(datadir.joinpath(filename)),
                '-user', self.user,
                '-password', self.password,
                '-delimit',  ',', ]

        if ldap:
            _cmd += ['-ldap', 'true']

        return _cmd

    def csvfiles(self, since, until, clean=False, delta=None):
        datadir = self._data_dir(since, until)

        if self._is_complete(datadir) and not clean:
            return list(datadir.glob('*.csv'))

        csv_files = []

        if delta is None:
            delta = 1

        for name, query in QueryMaker(since, until, delta, site=self.site, template=self.template).queries():
            # fast_export_cmd has a crappy way of dealing with auth errors, it will
            # complete with an error code of 0 and no error message, so you won't
            # actually know if it failed when you have an auth error
            fast_export_cmd = self._csvunloader(datadir, query, name)
            subprocess.run(fast_export_cmd, check=True, stdout=subprocess.PIPE)

            datafile = datadir.joinpath(name)
            if not datafile.exists():
                raise FastExportException(
                    '{datafile} was not created.'.format(datafile=datafile))

            csv_files.append(datafile)

        self._complete(datadir)

        return csv_files


class ExperimentDataSource(DataSource):

    @property
    def template(self):
        return TEMPLATE_BUYS
