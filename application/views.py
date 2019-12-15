from aiohttp import web

from application import storage


async def convert(request: web.Request) -> web.Response:
    currency_from = request.query.get('from')
    currency_to = request.query.get('to')
    amount = request.query.get('amount')
    try:
        amount = float(amount)
    except ValueError:
        raise web.HTTPBadRequest(reason='Query arg `amount` should be number')

    if not all((currency_from, currency_to)):
        raise web.HTTPBadRequest(reason='Query args `from` and `to` required')

    try:
        exchange_rate = await storage.get_exchange_rate(currency_from, currency_to)
    except ValueError:
        raise web.HTTPNotFound(reason=f'Exchange rate from `{currency_from}` to `{currency_to}` not found')
    result = round(exchange_rate * amount, 2)
    return web.json_response({'from': currency_from, 'to': currency_to, 'amount': amount, 'result': result})


async def database(request: web.Request) -> web.Response:
    data = await request.json()
    merge = bool(int(request.query.get('merge', '1')))
    await storage.update_exchange_rates(data, merge)
    return web.HTTPAccepted()
