from marshmallow import EXCLUDE, post_load
from marshmallow.fields import Decimal, Nested, String
from marshmallow.schema import Schema


class ConvertSchema(Schema):
    currency_from = String(data_key='from', required=True, allow_none=False)
    currency_to = String(data_key='to', required=True, allow_none=False)
    amount = Decimal(required=True, allow_none=False)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def post_load(self, data, **_):
        data['currency_from'] = data.pop('currency_from').upper()
        data['currency_to'] = data['currency_to'].upper()
        data['amount'] = float(round(data['amount'], 2))
        return data


class ExchangeRateSchema(Schema):
    _from = String(data_key='from', required=True, allow_none=False)
    to = String(required=True, allow_none=False)
    value = Decimal(required=True, allow_none=False)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def post_load(self, data, **_):
        data['from'] = data.pop('_from').upper()
        data['to'] = data['to'].upper()
        data['value'] = float(round(data['value'], 2))
        return data
