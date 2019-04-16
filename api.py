import asyncio
from aiohttp import web
from routes import setup_routes
from middlewares import compress_response
from utils import connection
import socket
import argparse

async def on_startup(app):
    pass

async def on_cleanup(app):
    pass

async def create_app(mongo_uri="mongodb://127.0.0.1:27017"):
    connection.setup_connection(mongo_uri)

    app = web.Application(middlewares=[compress_response.inject_compression])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    setup_routes(app)
    return app

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080, help='The port to run on')
    parser.add_argument('--ip', type=str, default=ip, help='The server ip')
    parser.add_argument('-m', '--mongo-uri', type=str, default="mongodb://127.0.0.1:27017", help='MongoDB uri')
    args = parser.parse_args()

    web.run_app(create_app(args.mongo_uri), host=args.ip, port=args.port)

    # docker run -d --name resetera-api -e 'VIRTUAL_PORT=8080' -e 'LETSENCRYPT_EMAIL=bjoern@friedrichs1.de' -e 'LETSENCRYPT_HOST=resetera.bjoern-friedrichs.de' -e 'VIRTUAL_HOST=resetera.bjoern-friedrichs.de' --link=mongodb:mongodb bfriedrichs/resetera