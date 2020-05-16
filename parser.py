import requests
from time import sleep
from threading import Thread
from traceback import print_exc
from requests import get
import random
import json
parseids = open('1.txt').read().split('\n')
proxies = open('proxies.txt').read().split('\n')


def generate_ua():
    ua = open('useragents.txt', 'r').read().split('\n')
    u = ua[random.randint(0, len(ua) - 1)]

    return u


def prx_convert(proxy_string):
    splitted = proxy_string.split(':')
    return splitted[2] + ':' + splitted[3] + '@' + splitted[0] + ':' + splitted[1]


def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def extract_information(user_id):
    """Get all the information for the given username."""
    uag = generate_ua()
    headers = {
        'User-Agent': uag,
    }
    proxy = random.choice(proxies)
    uproxy = {
        'http': 'http://' + prx_convert(proxy),
        'https': 'http://' + prx_convert(proxy)
    }
    try:
        resp = dict(
            requests.get('https://i.instagram.com/api/v1/users/{}/info/'.format(str(user_id)), headers=headers,
                         proxies=uproxy).json())
        username = resp['user']['username']
        profile = dict(get('https://www.instagram.com/{}/?__a=1'.format(username), proxies=uproxy).json())['graphql'][
            'user']
        photos = []
        caption = []
        likes = []
        root = profile['edge_owner_to_timeline_media']['edges']
        for node in root:
            photos.append(node['node']['display_url'])
            caption.append(node['node']['edge_media_to_caption']
                           ['edges'][0]['node']['text'])
            likes.append(node['node']['edge_liked_by']['count'])

        data = {
            'user_id': profile['id'],
            'avatar': profile['profile_pic_url_hd'],
            'full_name': profile['full_name'],
            'media_count': profile['edge_owner_to_timeline_media']['count'],
            'biography': profile['biography'],
            'follower_count': profile['edge_followed_by']['count'],
            'following_count': profile['edge_follow']['count'],
            'username': username,
            'last_post_at': root[0]['node']['taken_at_timestamp'],
            'photo_urls': photos,
            'caption': caption,
            'likes': likes
        }

        return data

    except Exception:
        return None


def savetotxt(jsondict):
    with open('100kparsed.txt', 'a', encoding='utf-8') as file:
        file.write(json.dumps(jsondict) + '\n')


def process_req_chunk(fromind, toind):
    for i in range(fromind, toind):
        data = extract_information(parseids[i])
        if data:
            savetotxt(data)


for i in range(2500000, 2550000, 1):
    Thread(target=process_req_chunk, args=(i, i + 1,)).start()
    sleep(0.1)
