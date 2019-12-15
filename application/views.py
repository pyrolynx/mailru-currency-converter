import marshmallow
from aiohttp import web

from application import storage, schemas, errors


@web.middleware
async def response_handler(request: web.Request, handler) -> web.Response:
    try:
        return web.json_response({"status": "ok", "result": await handler(request)})
    except (errors.APIError, marshmallow.ValidationError) as e:
        return web.json_response({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)


async def convert(request: web.Request) -> dict:
    data = schemas.ConvertSchema().load(request.query)
    currency_from = data['currency_from']
    currency_to = data['currency_to']
    try:
        exchange_rate = await storage.get_exchange_rate(currency_from, currency_to)
    except ValueError:
        raise errors.EntityNotFound(f'Exchange rate from `{currency_from}` to `{currency_to}` not found')
    result = round(exchange_rate * data['amount'], 2)
    return result


async def database(request: web.Request) -> bool:
    data = schemas.ExchangeRateSchema().load(await request.json(), many=True)
    merge = request.query.get('merge')
    if merge not in ('0', '1'):
        raise marshmallow.ValidationError('arg `merge` can be set to 0 or 1')
    merge = bool(int(merge))
    await storage.update_exchange_rates(data, merge)
    return True
