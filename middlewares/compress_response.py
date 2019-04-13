import gzip
from aiohttp import web
import sys

@web.middleware
async def inject_compression(request, handler):
    response = await handler(request)

    if 'compressed' in request.query and request.query['compressed'] not in (False, 0, '0'):
        resp = gzip.compress(response.body)
        headers = {
            'Content-type': 'application/octet-stream',
            'Content-encoding': 'gzip'
        }
        return web.Response(body=resp, headers=headers, status=response.status)

    return response