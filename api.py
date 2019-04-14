import asyncio
from aiohttp import web
from routes import setup_routes
from middlewares import compress_response
import ssl
import yaml
import os

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
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

        sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslcontext.load_cert_chain(os.path.join(cfg['ssl']['path'], 'cert.pem'), os.path.join(cfg['ssl']['path'], 'key.pem'))
        web.run_app(create_app(), host='127.0.0.1', port=443)

    # docker run -d --name resetera-api -v /root:/root -e 'LETSENCRYPT_EMAIL=bjoern@friedrichs1.de' -e 'LETSENCRYPT_HOST=resetera.bjoern-friedrichs.de' -e 'VIRTUAL_HOST=resetera.bjoern-friedrichs.de' bfriedrichs/resetera