from bs4 import BeautifulSoup
import aiohttp
from utils import api_response, constants

async def index(request):
    result = []

    async with aiohttp.ClientSession() as session:
        async with session.get(constants.BASE_URL) as resp:
            html_doc = await resp.text()
            soup = BeautifulSoup(html_doc, 'html.parser')
            nodes = soup.find_all(class_='node')
            for node in nodes:
                link = node.find(class_='node-title').find('a')
                url = link['href']
                url_id = url.replace('/forums/', '')[:-1]

                forum = {
                    'name': link.getText(),
                    'url': url,
                    'id': url_id
                }
                result.append(forum)

    response = api_response.Response(result)
    return response.build_response()

async def list_threads(request):
    forum_id = request.match_info['forum_id']
    result = []

    async with aiohttp.ClientSession() as session:
        forum_url = '{}forums/{}'.format(constants.BASE_URL, forum_id)
        async with session.get(forum_url) as resp:
            html_doc = await resp.text()
            soup = BeautifulSoup(html_doc, 'html.parser')
            nodes = soup.find_all(class_='structItem')
            for node in nodes:
                link = node.find(class_='structItem-title').find('a')
                url = link['href']
                url_id = url.replace('/threads/', '')[:-1]

                forum = {
                    'name': link.getText(),
                    'url': url,
                    'id': url_id
                }
                result.append(forum)

    response = api_response.Response(result)
    return response.build_response()
