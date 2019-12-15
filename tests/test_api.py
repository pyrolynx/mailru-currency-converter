import contextlib
import random

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


@pytest.fixture
def redis_get_exchange_rate(redis):
    async def get_exchange_rate(rate):
        with (await redis) as conn:
            return await conn.get(f'{rate._from}:{rate._to}')
    return get_exchange_rate


async def test_currency_convert(api_client: TestClient, exchange_rate: ExchangeRate, storage):
    amount = round(random.random() * 1000, 2)
    async with storage(exchange_rate):
        response = await api_client.get('/convert', params={
            'from': exchange_rate._from,
            'to': exchange_rate._to,
            'amount': str(amount)})
        assert response.status == 200
        response_json = await response.json()
        assert response_json['status'] == 'ok'
        assert response_json['result'] == round(amount * exchange_rate.value, 2)


@pytest.mark.parametrize('upd_params', [{'from': 'FOO'}, {'to': 'BAR'}, {'from': 'FOO', 'to': 'BAR'}])
async def test_currency_convert__unknown_currency(api_client: TestClient, exchange_rate: ExchangeRate, storage,
                                                  upd_params: dict):
    amount = round(random.random() * 1000, 2)
    params = {
        'from': exchange_rate._from,
        'to': exchange_rate._to,
        'amount': str(amount)
    }
    params.update(upd_params)
    async with storage(exchange_rate):
        response = await api_client.get('/convert', params=params)
        assert response.status == 400
        response_json = await response.json()
        assert response_json['status'] == 'error'


async def test_database_store(api_client: TestClient):
    rates = [ExchangeRate() for x in range(4)]
    response = await api_client.post('/database', params={'merge': 1}, json=rates)
    assert response.status == 200
    response_json = await response.json()
    assert response_json['status'] == 'ok'
    assert response_json['result'] == True


async def test_database_store_drop_old_keys(api_client: TestClient, exchange_rate: ExchangeRate, storage,
                                            redis_get_exchange_rate):
    async with storage(exchange_rate):
        new = ExchangeRate()
        response = await api_client.post('/database', params={'merge': 0}, json=[new])
        assert response.status == 200
        response_json = await response.json()
        assert response_json['status'] == 'ok'
        assert response_json['result'] == True
        assert await redis_get_exchange_rate(exchange_rate) is None