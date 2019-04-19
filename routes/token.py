from utils import api_response, constants, connection

async def register_token(request):
    result = {"ok": True}

    coll = connection.get_collection("PushToken")

    body = await request.json()
    if 'token' not in body:
        response = api_response.Response(result, status=400, message="'token' key is required")
        return response.build_response()

    token = body['token']
    data = {
        'token': token
    }
    exists = coll.find_one(data)
    if not exists:
        data['trending_active'] = True
        data['new_active'] = True
        data['new_threads'] = { '7': True}
        coll.insert_one(data)

    response = api_response.Response(result)
    return response.build_response()

async def config(request):
    result = {"ok": False}
    body = await request.json()

    if 'token' not in body or 'config' not in body:
        response = api_response.Response(result, status=400, message="'token' and 'config' keys are required")
        return response.build_response()

    config = body['config']
    new_threads = config.get('new_threads', None)
    new_active = config.get('new_active', None)
    trending_active = config.get('trending_active', None)

    data = {}

    if trending_active is not None:
        if type(trending_active) != bool:
            response = api_response.Response(result, status=400, message="'trending_active' has to be of bool type")
            return response.build_response()
        data['trending_active'] = trending_active

    if new_active is not None:
        if type(new_active) != bool:
            response = api_response.Response(result, status=400, message="'new_active' has to be of bool type")
            return response.build_response()
        data['new_active'] = new_active

    if new_threads is not None:
        if type(new_threads) != dict:
            response = api_response.Response(result, status=400, message="'new_threads' has to be of dict type")
            return response.build_response()

        for key, val in new_threads.items():
            if type(key) != str:
                response = api_response.Response(result, status=400, message="keys have to be of str type")
                return response.build_response()
            if type(val) != bool:
                response = api_response.Response(result, status=400, message="values have to be of bool type")
                return response.build_response()
        data['new_threads'] = new_threads

    if len(data) == 0:
        response = api_response.Response(result, status=400, message="Cannot update with no changes")
        return response.build_response()

    coll = connection.get_collection("PushToken")
    update = coll.update_one({'token': body['token']}, {
        '$set': data
    })

    result['config'] = config
    result['ok'] = True
    response = api_response.Response(result)
    return response.build_response()
