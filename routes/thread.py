from bs4 import BeautifulSoup
import aiohttp
from utils import api_response, constants
import re

def clean_attrs(tag, whitelist=[]):
    attrs = tag.attrs.copy()
    for attr in attrs:
        if attr not in whitelist:
           del tag[attr]

def parse_content(content):
    images = content.find_all('img')
    for i in images:
        i.name = "Image"
        clean_attrs(i, ['src'])

    bolds = content.find_all('b')
    for b in bolds:
        b.name = "Bold"

    links = content.find_all('a')
    for a in links:
        if a.has_attr("href"):
            a.name = "LinkTo"
            clean_attrs(a, ['href'])

            if a['href'].startswith(constants.BASE_URL):
                a['type'] = "internal"
                base_regex = constants.BASE_URL.replace("/", "\/").replace(".", "\\.")
                if "/threads/" in a['href']:
                    a['target'] = "thread"
                    a['id'] = re.sub(base_regex + r"threads\/([^\/]*)", "\g<1>", a['href'])[:-1]
                elif "/forums/" in a['href']:
                    a['target'] = "forum"
                    a['id'] = re.sub(base_regex + r"forum\/([^\/]*)", "\g<1>", a['href'])[:-1]
            else:
                a['type'] = "external"
        else:
            # remove "Click to expand"
            a.decompose()

    lists = content.find_all('ul')
    for l in lists:
        l.name = "TextList"
        clean_attrs(l)

    ordered_lists = content.find_all('ol')
    for l in ordered_lists:
        l.name = "TextList"
        clean_attrs(l)
        l['type'] = "ordered"

    list_items = content.find_all('li')
    for li in list_items:
        li.name = "TextListItem"
        clean_attrs(li)

    blocks = content.find_all(class_="bbCodeBlock")
    for b in blocks:
        title = b.find(class_="bbCodeBlock-title")
        if title:
            title.name = "BlockTitle"
            clean_attrs(title)

        b.name = "Block"
        clean_attrs(b)

    result = str(content)
    result = re.sub(r"(?:\n)+", "", result, flags=re.MULTILINE)
    result = re.sub(r"(<br>|<br/>)", "\n", result, flags=re.MULTILINE)
    result = re.sub(r"<(?!\/?(Image|Bold|LinkTo|TextList|TextListItem|Block|BlockTitle))[^>]*>", "", result, flags=re.MULTILINE)

    soup = BeautifulSoup(result, 'html.parser')

    def create_tree(curr_node):
        childs = list(curr_node.children)
        if len(childs) == 0:
            return [{"type": "text", "content": curr_node.getText()}]
        else:
            tree = []
            for child in childs:
                if child.name:
                    name = child.name
                    leaf = {"type": name, "content": create_tree(child)}
                    if len(child.attrs) > 0:
                        leaf["attrs"] = child.attrs
                    if name == "linkto":
                        leaf['attrs']['textOnly'] = all([x['type'] in ("text", "bold") for x in leaf['content']])
                    tree.append(leaf)
                else:
                    tree.append({"type": "text", "content": str(child)})
            return tree

    def shallow_group_text(tree):
        curr_group = []
        groups = []
        for n in tree:
            if n['type'] in ("text", "bold") or n['type'] in ("linkto") and n['attrs']['textOnly']:
                curr_group.append(n)
            else:
                groups.append({"type": "textgroup", "content": curr_group.copy()})
                curr_group = []
                groups.append(n)
        if len(curr_group) > 0:
            groups.append({"type": "textgroup", "content": curr_group.copy()})
        return groups

    def deep_group_text(tree):
        curr_group = []
        groups = []
        for n in tree:
            if n['type'] in ("text", "bold") or n['type'] in ("linkto") and n['attrs']['textOnly']:
                curr_group.append(n)
            else:
                if len(curr_group) > 0:
                    groups.append({"type": "textgroup", "content": curr_group.copy()})
                curr_group = []
                n['content'] = deep_group_text(n['content'])
                groups.append(n)
        if len(curr_group) > 0:
            groups.append({"type": "textgroup", "content": curr_group.copy()})
        return groups

    def test_non_text(ct, path, is_text=False):
        for i in range(len(ct)):
            c = ct[i]
            if c['type'] == "text":
                continue

            curr_path = path.copy()
            curr_path.append(i)
            if c['type'] in ("textgroup", "bold") or c["type"] == "linkto" and c['attrs']['textOnly']:
                new_path = test_non_text(c['content'], curr_path, True)
                if new_path is not None:
                    return new_path
            else:
                if is_text:
                    return curr_path
                else:
                    new_path = test_non_text(c['content'], curr_path, False)
                    if new_path is not None:
                        return new_path
        return None

    def split_by_issue(tree, issue):
        head = tree[:issue[0]]
        mid = []
        tail = tree[issue[0]+1:]
        if len(issue) > 1:
            mid_head, mid_mid, mid_tail = split_by_issue(tree[issue[0]]['content'], issue[1:])

            head = head + mid_head
            mid = mid_mid
            tail = mid_tail + tail
        else:
            mid = [tree[issue[0]]]
        return head, mid, tail

    result = create_tree(soup)

    while True:
        issue = test_non_text(result, [])
        if issue is None:
            break

        head, mid, tail = split_by_issue(result, issue)
        result = head + mid + tail
    result = deep_group_text(result)

    return result

async def list_comments(request):
    thread_id = request.match_info['thread_id']
    result = {}

    async with aiohttp.ClientSession() as session:
        thread_url = '{}threads/{}'.format(constants.BASE_URL, thread_id)
        async with session.get(thread_url) as resp:
            html_doc = await resp.text()
            soup = BeautifulSoup(html_doc, 'html.parser')
            nodes = soup.find_all(class_='message')
            posts = []
            for node in nodes:
                user = node.find(class_='message-user')
                name = user.find(class_='username').getText()

                img = user.find(class_='message-avatar').img
                avatar = img['src'] if img else ""

                date = node.find(class_='u-dt').getText()
                content = node.find(class_='message-content')

                forum = {
                    'id': node['data-content'],
                    'content': parse_content(content),
                    'date': date,
                    'user': {
                      'name': name,
                      'avatar': avatar
                    }
                }
                posts.append(forum)
            bcrumbs = soup.find(class_="p-breadcrumbs")
            last = bcrumbs.find_all("li")[-1]
            url = last.find("a")['href']
            url_id = url.replace('/forums/', '')[:-1]
            result['posts'] = posts
            result['forumId'] = url_id
            meta = {
                "name": soup.find(class_="p-title-value").getText(),
                "url": thread_url,
                "id": thread_id
            }
            result['meta'] = meta

    response = api_response.Response(result)
    return response.build_response()
