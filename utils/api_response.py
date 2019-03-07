from aiohttp import web

class Response:
    def __init__(self, payload, status=200, message="ok"):
        self.payload = payload
        self.status = status
        self.message = message

    def build_response(self):
        resp = {
            "message": self.message,
            "payload": self.payload
        }
        return web.json_response(resp, status=self.status)