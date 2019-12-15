import aioredis

from application import config

redis: aioredis.Redis = None


async def init_redis():
    global redis
    redis = await aioredis.create_redis(
        address=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}',
        password=config.REDIS_PASS)
    return redis


async def get_exchange_rate(currency_from: str, currency_to: str) -> float:
    with (await redis) as conn:
        value = await conn.get(f'{currency_from}:{currency_to}')
    if value is None:
        raise ValueError
    return float(value)


async def update_exchange_rates(data: list, merge: bool = True):
    with (await redis) as conn:
        transaction = conn.multi_exec()
        if not merge:
            transaction.flushdb()
        for exchange_rate in data:
            transaction.set(f'{exchange_rate["from"]}:{exchange_rate["to"]}', float(exchange_rate["value"]))
        await transaction.execute()
