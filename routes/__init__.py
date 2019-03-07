from aiohttp import web
from routes import forum, thread
from utils import api_response

def hello(request):
    response = api_response.Response({"ok": True})
    return response.build_response()

def setup_routes(app):
    app.router.add_get('/', hello)
    app.router.add_get('/forum', forum.index)
    app.router.add_get('/forum/{forum_id}', forum.list_threads)
