from bs4 import BeautifulSoup
import aiohttp
from utils import api_response, constants, parse_content, parse_poll

async def list_posts(request):
    thread_id = request.match_info['thread_id']
    page = int(request.match_info.get('page', 1))
    result = {}

    async with aiohttp.ClientSession() as session:
        thread_url = '{}threads/{}/page-{}'.format(constants.BASE_URL, thread_id, page)
        async with session.get(thread_url) as resp:
            html_doc = await resp.text()
            soup = BeautifulSoup(html_doc, 'html.parser')
            nodes = soup.find_all(class_='message')
            posts = []
            for node in nodes:
                user = node.find(class_='message-user')
                name = user.find(class_='username').get_text()

                img = user.find(class_='message-avatar').img
                avatar = img['src'] if img else ""

                date = node.find(class_='u-dt').get_text()
                content = node.find(class_='message-content')

                post = {
                    'id': int(node['data-content'].split('-')[-1]),
                    'content': parse_content.parse_content(content),
                    'date': date,
                    'user': {
                      'name': name,
                      'avatar': avatar
                    }
                }
                posts.append(post)

            poll = soup.find(class_="p-body-pageContent").findChildren("form", recursive=False)
            if poll:
                result['poll'] = parse_poll.parse_poll(poll[0])

            bcrumbs = soup.find(class_="p-breadcrumbs")
            last = bcrumbs.find_all("li")[-1]
            url = last.find("a")['href']
            url_id = url.replace('/forums/', '')
            if url_id.endswith('/'):
                url_id = url_id[:-1]
            url_id = url_id.split('.')[-1]

            result['posts'] = posts
            result['forumId'] = url_id

            pages = 1
            nav = soup.find(class_="pageNav-main")
            if nav is not None:
                nav_items = nav.find_all(class_="pageNav-page")
                last_nav_item = nav_items[-1]
                pages = int(last_nav_item.get_text())

            meta = {
                "name": soup.find(class_="p-title-value").get_text(),
                "url": thread_url,
                "pages": pages
            }
            result['id'] = int(thread_id)
            result['page'] = page
            result['meta'] = meta

    response = api_response.Response(result)
    return response.build_response()
