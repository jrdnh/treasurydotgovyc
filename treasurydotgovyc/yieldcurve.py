from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser
import requests
import numpy as np
import lxml.etree as etree
import lxml.objectify as objectify


_term_offsets = {
    'BC_1MONTH': relativedelta(months=1),
    'BC_2MONTH': relativedelta(months=2),
    'BC_3MONTH': relativedelta(months=3),
    'BC_6MONTH': relativedelta(months=6),
    'BC_1YEAR': relativedelta(months=12),
    'BC_2YEAR': relativedelta(months=24),
    'BC_3YEAR': relativedelta(months=36),
    'BC_5YEAR': relativedelta(months=60),
    'BC_7YEAR': relativedelta(months=84),
    'BC_10YEAR': relativedelta(months=120),
    'BC_20YEAR': relativedelta(months=240),
    'BC_30YEAR': relativedelta(months=360)
}


class YieldCurve:

    url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/XmlView.aspx?data=yield'
    entry_ns = '{http://www.w3.org/2005/Atom}'
    property_ns = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}'
    ENTRY = 'entry'
    CONTENT = 'content'
    PROPERTIES = 'properties'

    def __init__(self):
        self._as_of_date = None
        self._yield_curve = self._load_yield_curve()

    @property
    def as_of_date(self):
        return self._as_of_date

    @property
    def yield_curve(self):
        return self._yield_curve

    def update_yield_curve(self):
        self._yield_curve = self._load_yield_curve()

    def _load_yield_curve(self):
        content = self.get_data_from_treasury()
        points = self.parse_response(content)
        return points

    def get_data_from_treasury(self):
        r = requests.get(self.url)
        if r.ok:
            return r.content
        else:
            raise Exception('Bad response from Treasury.gov.')

    def parse_response(self, content):
        tree = objectify.fromstring(content)
        last_entry = self.get_entries(tree)[-1]
        content = self.get_content(last_entry)
        properties = self.get_properties(content)

        self._as_of_date = dateutil.parser.isoparse(str(properties['{http://schemas.microsoft.com/ado/2007/08/dataservices}NEW_DATE']))

        yc = self.get_yc_values(properties)
        return yc

    def get_entries(self, tree):
        return list(tree.iterchildren(tag=self.entry_ns + self.ENTRY))

    def get_content(self, entry):
        return entry[self.CONTENT]

    def get_properties(self, content):
        return content[self.property_ns + self.PROPERTIES]

    def get_yc_values(self, properties):
        values = properties.getchildren()[2:-1]
        return {self.strip_prop_ns(v.tag): v.pyval / 100 for v in values}

    def strip_prop_ns(self, tag):
        return tag.replace('{http://schemas.microsoft.com/ado/2007/08/dataservices}', '')

    def yield_for_delta(self, delta):
        x_day = self._as_of_date + delta
        return self.yield_for_date(x_day)

    def yield_for_date(self, dt):
        x_day = dt.toordinal()
        yc = {(self._as_of_date + _term_offsets[k]).toordinal(): v for k, v in self.yield_curve.items()}

        return np.interp(x_day, list(yc.keys()), list(yc.values()))

