import asyncio
import aiohttp
from utils import constants, connection, send_push
from bs4 import BeautifulSoup
import argparse

async def send_notification(thread, filt={}):
    coll = connection.get_collection("PushToken")
    tokens = list(coll.find(filt))
    print("Sending to {} clients".format(len(tokens)))
    for token in tokens:
        send_push.send_push_message(token['token'], thread['title'], thread['body'], thread)

async def parse_threads(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(constants.BASE_URL + url) as resp:
            html_doc = await resp.text()
            soup = BeautifulSoup(html_doc, 'html.parser')
            node = soup.find(class_="structItem")

            link = node.find(class_="structItem-title").find('a')
            title = link.getText()
            url = link['href']
            url_id = url.replace('/threads/', '')
            if url_id.endswith('/'):
                url_id = url_id[:-1]
            url_id = url_id.split('.')[-1]

            category = node.find(class_="structItem-parts").find_all('a')[-1]['href']
            cat_id = None
            if category.startswith('/forums/'):
                cat_id = category.replace('/forums/', '')
                if cat_id.endswith('/'):
                    cat_id = cat_id[:-1]
                cat_id = cat_id.split('.')[-1]

            thread = {
                'id': url_id,
                'body': title,
                'type': 'thread',
                'category': cat_id
            }
            return thread

async def periodic(wait_time, once=False, ignore_cache=False):
    while True:
        print("Begin parse")
        thread = await parse_threads('trending/threads.1/')
        print("Found trending: {}".format(thread['id']))

        thread['title'] = "New Trending Thread"
        trending_thread_filter = {'trending_active': True}
        if ignore_cache:
            await send_notification(thread, trending_thread_filter)
        else:
            trending_cache = connection.get_collection("TrendingCache")
            filt = {'thread_id': thread['id']}
            hit = trending_cache.find_one(filt)
            if not hit:
                trending_cache.insert_one(filt)
                await send_notification(thread, trending_thread_filter)

        thread = await parse_threads('forums/-/latest-threads/')
        print("Found new: {}".format(thread['id']))

        thread['title'] = "New Thread"
        new_thread_filter = {
            'new_active': True,
            'new_threads.{}'.format(thread['category']): True
        }
        if ignore_cache:
            await send_notification(thread, new_thread_filter)
        else:
            thread_cache = connection.get_collection("ThreadCache")
            filt = {'thread_id': thread['id']}
            hit = thread_cache.find_one(filt)
            if not hit:
                thread_cache.insert_one(filt)
                await send_notification(thread, new_thread_filter)
        if once:
            break
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--once', action='store_true',  default=False, help='Exec only once')
    parser.add_argument('-i', '--ignore-cache', action='store_true', default=False, help='Ignore previous cache')
    parser.add_argument('-w', '--wait-time', type=int, default=300, help='Time between rechecking')

    parser.add_argument('-m', '--mongo-uri', type=str, default="mongodb://localhost:27017", help='MongoDB uri')
    args = parser.parse_args()

    connection.setup_connection(args.mongo_uri)

    loop = asyncio.get_event_loop()
    task = loop.create_task(periodic(args.wait_time, once=args.once, ignore_cache=args.ignore_cache))

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError as err:
        print(err)

    # docker run -d --name resetera-api-push --link=mongodb:mongodb bfriedrichs/resetera-push