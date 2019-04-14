import asyncio
import aiohttp
from utils import constants, connection, send_push
from bs4 import BeautifulSoup
import sys

WAIT_TIMER = 60 * 10

async def send_notification(thread):
    coll = connection.get_collection("PushToken")
    tokens = coll.find({})

    for token in tokens:
        send_push.send_push_message(token['value'], thread['title'], thread)

async def parse_trending():
    async with aiohttp.ClientSession() as session:
        async with session.get(constants.BASE_URL + 'trending/threads.1/') as resp:
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

            thread = {
                'id': url_id,
                'title': title,
                'type': 'trending_thread'
            }
            return thread

async def periodic(wait_time, times=0, ignore_cache=False):
    i = 0
    while True:
        thread = await parse_trending()
        if ignore_cache:
            await send_notification(thread)
        else:
            thread_cache = connection.get_collection("ThreadCache")
            filt = {'thread_id': thread['id']}
            hit = thread_cache.find_one(filt)
            if not hit:
                thread_cache.insert_one(filt)
                await send_notification(thread)
        i += 1
        if times != 0 and i == times:
            break
        await asyncio.sleep(wait_time)

def stop():
    task.cancel()

if __name__ == "__main__":
    times = 0
    if len(sys.argv) > 1:
        times = int(sys.argv[1])
    loop = asyncio.get_event_loop()
    loop.call_later(5, stop)
    task = loop.create_task(periodic(WAIT_TIMER, times))

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass