import contextlib
import random
from collections import namedtuple

import pytest
from aiohttp.test_utils import TestClient


class ExchangeRate(dict):
    def __init__(self, _from: str = None, _to: str = None, value: float = None):
        super().__init__()
        self['from'] = _from or random.choice(currencies)
        self['to'] = _to or random.choice(currencies)
        self['value'] = float(value) if value else round(random.random() * 100, 2)

    @property
    def _from(self):
        return self['from']

    @property
    def _to(self):
        return self['to']

    @property
    def value(self):
        return self['value']


currencies = ['RUR', 'EUR', 'USD', 'IPA']


@pytest.fixture
def exchange_rate():
    return ExchangeRate()


@pytest.fixture
def storage(redis):
    @contextlib.asynccontextmanager
    async def store_exchange_rate(rate: ExchangeRate):
        with (await redis) as conn:
            await conn.set(f'{rate._from}:{rate._to}', rate.value)
            yield
            await conn.delete(f'{rate._from}:{rate._to}')

    return store_exchange_rate

@pytest.mark.asyncio
async def test_currency_convert(api_client: TestClient, exchange_rate: ExchangeRate, storage):
    amount = round(random.random() * 1000, 2)
    async with storage(exchange_rate):
        response = await api_client.get('/convert', params={
            'from': exchange_rate._from,
            'to': exchange_rate._to,
            'amount': str(amount)})
        response_json = await response.json()
        assert response_json['status'] == 'ok'
        assert response_json['result'] == round(amount * exchange_rate.value, 2)
