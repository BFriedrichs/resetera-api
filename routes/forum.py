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
                desc = node.find(class_='node-description')
                url = link['href']
                url_id = url.replace('/forums/', '')
                if url_id.endswith('/'):
                    url_id = url_id[:-1]
                url_id = url_id.split('.')[-1]

                meta = {
                    'name': link.get_text(),
                    'desc': desc.get_text(),
                    'url': url,
                }

                forum = {
                    'meta': meta,
                    'id': int(url_id)
                }
                result.append(forum)

    response = api_response.Response(result)
    return response.build_response()

async def list_threads(request):
    forum_id = request.match_info['forum_id']
    page = int(request.match_info.get('page', 1))
    result = {}

    async with aiohttp.ClientSession() as session:
        forum_url = '{}forums/{}/page-{}'.format(constants.BASE_URL, forum_id, page)
        async with session.get(forum_url) as resp:
            html_doc = await resp.text()
            soup = BeautifulSoup(html_doc, 'html.parser')
            nodes = soup.find_all(class_='structItem')
            threads = []
            for node in nodes:
                link = node.find(class_='structItem-title').find('a')
                url = link['href']
                url_id = url.replace('/threads/', '')
                if url_id.endswith('/'):
                    url_id = url_id[:-1]
                url_id = url_id.split('.')[-1]

                jump = node.find(class_='structItem-pageJump')
                pages = 1
                if jump:
                    last_page = jump.find_all('a')[-1]
                    pages = int(last_page.get_text())

                sticky = False
                if node.parent['class'] == 'structItemContainer-group--sticky':
                    sticky = True

                date = node.find(class_='u-dt').get_text()
                latestDate = node.find(class_='structItem-latestDate').get_text()

                status_nodes = node.find_all(class_='structItem-status')
                statuses = [s['title'].lower() for s in status_nodes]

                view_node = node.find(class_="structItem-statuses")
                pair = view_node.find_all('dd')
                view_count = pair[0].get_text()
                post_count = pair[1].get_text()

                thread = {
                    'meta': {
                        'name': link.get_text(),
                        'url': url,
                        'pages': pages
                    },
                    'id': int(url_id),
                    'date': date,
                    'latest_date': latestDate,
                    'statuses': statuses,
                    'view_count': view_count,
                    'post_count': post_count
                }
                threads.append(thread)

            result['threads'] = threads

            pages = 1
            nav = soup.find(class_="pageNav-main")
            if nav is not None:
                nav_items = nav.find_all(class_="pageNav-page")
                last_nav_item = nav_items[-1]
                pages = int(last_nav_item.get_text())

            meta = {
                "name": soup.find(class_="p-title-value").get_text(),
                "url": forum_url,
                'pages': pages
            }
            result['meta'] = meta
            result['id'] = forum_id
            result['page'] = page

    response = api_response.Response(result)
    return response.build_response()
