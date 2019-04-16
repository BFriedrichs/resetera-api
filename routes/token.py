from utils import api_response, constants, connection

async def register_token(request):
    result = {"ok": True}

    coll = connection.get_collection("PushToken")

    body = await request.json()
    token = body['token']

    exists = coll.find_one(token)
    if not exists:
        token['active'] = True
        coll.insert_one(token)

    response = api_response.Response(result)
    return response.build_response()

async def set_active(request):
    result = {"ok": False}

    coll = connection.get_collection("PushToken")

    body = await request.json()
    if 'token' not in body or 'active' not in body:
        response = api_response.Response(result, status=400, message="'token' and 'active' keys are required")
        return response.build_response()

    if type(body['active']) != bool:
        response = api_response.Response(result, status=400, message="'active' has to be of bool type")
        return response.build_response()

    update = coll.update_one({'token': body['token']}, {'$set': {'active': body['active']}})

    response = None
    if update.matched_count == 1:
        response = api_response.Response(result)
    else:
        response = api_response.Response(result, status=400)
    return response.build_response()