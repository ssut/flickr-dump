import sys
if sys.version_info < (3, 4):
    raise Exception('')
    exit(1)

import asyncio
import functools
import flickrapi
import itertools
import os

def dump(api, secret, user_id, target='./data'):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_dump(api, secret, user_id, target))
    loop.close()

def _dump(api, secret, user_id, target):
    flickr = flickrapi.FlickrAPI(api, secret, format='parsed-json')
    pages = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=1)['photos']['pages']
    print('Total page to download:', pages)

    coros = []
    for i in range(pages):
        coros.append(asyncio.Task(_get_urls(flickr, user_id, i + 1)))

    urls = yield from asyncio.gather(*coros)
    urls = list(itertools.chain.from_iterable(urls))
    print('Total photos to download:', len(urls))

    download(urls, target)

def download(urls, target):
    if not os.path.exists(target):
        os.makedirs(target)
    for i, url in enumerate(urls):
        asyncio.async(_download(url, target))

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

@asyncio.coroutine
def _get_urls(flickr, user_id, p):
    items = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=p)['photos']['photo']
    
    urls = []
    for i, item in enumerate(items):
        item_id, item_secret = item.get('id'), item.get('secret')
        res = yield from asyncio.async(_get_url(flickr, item_id, item_secret))
        urls.append(res)

    return urls

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
