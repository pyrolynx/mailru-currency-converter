from application import views, config

from aiohttp import web


async def prepare_startup(app: web.Application):
    from application import storage
    app['redis'] = await storage.init_redis()


async def prepare_shutdown(app: web.Application):
    app['redis'].close()
    await app['redis'].wait_closed()


def get_app() -> web.Application:
    app = web.Application()
    app.middlewares.append(views.response_handler)
    app.router.add_get('/convert', views.convert)
    app.router.add_post('/database', views.database)
    app.on_startup.append(prepare_startup)
    app.on_shutdown.append(prepare_startup)

    return app


if __name__ == '__main__':
    app = get_app()
    web.run_app(app, host=config.HOST, port=config.PORT)