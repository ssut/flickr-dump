import sys
if sys.version_info < (3, 4):
    raise Exception('')
    exit(1)

import asyncio
import aiohttp
import functools
import flickrapi
import itertools
import os

def dump(api, secret, user_id, target='./data'):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_dump(api, secret, user_id, target))
    loop.close()

def _dump(api, secret, user_id, target):
    if not os.path.exists(target):
        os.makedirs(target)

    flickr = flickrapi.FlickrAPI(api, secret, format='parsed-json')
    pages = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=1)['photos']['pages']
    print('Total pages to download:', pages)

    coros = []
    for i in range(pages):
        coros.append(asyncio.Task(_get_urls(flickr, user_id, i + 1, target)))

    yield from asyncio.gather(*coros)

@asyncio.coroutine
def _download(url, target):
    filename = url.split('/')[-1]
    print(filename, 'downloading')
    target = '{}/{}'.format(target, filename)
    r = yield from aiohttp.request('get', url)
    with open(target, 'wb') as fd:
        while True:
            chunk = yield from r.content.read(1024)
            if not chunk:
                break
            fd.write(chunk)
    r.close()

@asyncio.coroutine
def _get_urls(flickr, user_id, p, target):
    items = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=p)['photos']['photo']
    count = len(items)

    for i, item in enumerate(items):
        item_id, item_secret = item.get('id'), item.get('secret')
        res = yield from asyncio.async(_get_url(flickr, item_id, item_secret))
        asyncio.async(_download(res, target))

    return count

@asyncio.coroutine
def _get_url(flickr, item_id, item_secret):
    loop = asyncio.get_event_loop()
    sizes_callback = functools.partial(flickr.photos.getSizes, photo_id=item_id)
    sizes = loop.run_in_executor(None, sizes_callback)
    sizes = yield from sizes

    sizes = sizes.get('sizes').get('size')
    original = ''
    try:
        original = next(d for (idx, d) in enumerate(sizes) if d['label'] == 'Original')
    except: pass

    return original.get('source', '')
