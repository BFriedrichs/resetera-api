import asyncio
from aiohttp import web
from routes import setup_routes
from middlewares import compress_response

async def on_startup(app):
    pass

async def on_cleanup(app):
    pass


async def create_app():
    app = web.Application(middlewares=[compress_response.inject_compression])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    setup_routes(app)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host='127.0.0.1', port=80)