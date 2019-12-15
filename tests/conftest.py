import pytest
from aiohttp.test_utils import TestClient

from main import get_app


@pytest.fixture
def api_client(loop, aiohttp_client) -> TestClient:
    return loop.run_until_complete(aiohttp_client(get_app()))


@pytest.fixture
def redis(api_client):
    return api_client.app['redis']
