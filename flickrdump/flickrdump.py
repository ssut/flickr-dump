import sys
if sys.version_info < (3, 4):
    raise Exception('')
    exit(1)

import asyncio
import functools
import flickrapi
import itertools

def dump(api, secret, user_id, target='.data'):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_dump(api, secret, user_id, target))
    loop.close()

def _dump(api, secret, user_id, target):
    flickr = flickrapi.FlickrAPI(api, secret, format='parsed-json')
    pages = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=1)['photos']['pages']

    coros = []
    for i in range(pages):
        coros.append(asyncio.Task(_get_urls(flickr, user_id, i + 1)))

    urls = yield from asyncio.gather(*coros)
    urls = list(itertools.chain.from_iterable(urls))

    download(urls)

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
