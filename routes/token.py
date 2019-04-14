from utils import api_response, constants, connection

async def register_token(request):
    result = {"ok": True}

    coll = connection.get_collection("PushToken")

    body = await request.json()
    token = body['token']

    exists = coll.find_one(token)
    if not exists:
        coll.insert_one(token)

    response = api_response.Response(result)
    return response.build_response()