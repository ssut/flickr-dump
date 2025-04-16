import sys
import asyncio
import aiohttp
import functools
import flickrapi
import os

COUNT_LOCK = asyncio.Lock()
COUNT_DLS = [0, 0]

async def dump(api, secret, user_id, target='./data'):
    try:
        loop = asyncio.get_event_loop()
        await _dump(api, secret, user_id, target)
    except OSError:
        return 1
    except KeyboardInterrupt:
        print('Stopped')

    return 0

async def _dump(api, secret, user_id, target):
    if not os.path.exists(target):
        os.makedirs(target)

    flickr = flickrapi.FlickrAPI(api, secret, format='parsed-json')
    pages = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=1)['photos']['pages']
    print('Total pages to download:', pages)

    coros = [asyncio.create_task(_get_urls(flickr, user_id, i + 1, target)) for i in range(pages)]
    await asyncio.gather(*coros)
    sys.stdout.write('\n')
    print('done!')

async def _count(i, incr=False):
    global COUNT_DLS
    async with COUNT_LOCK:
        if incr:
            COUNT_DLS[i] += 1
        return COUNT_DLS[i]

async def _download(url, target):
    filename = url.split('/')[-1]

    dl = await _count(1, True)
    cnt = await _count(0)
    sys.stdout.write('[{}/{}, {:.02f}%] Downloading..\r'.format(
        cnt, dl, (cnt / dl * 100.0)))
    sys.stdout.flush()

    target_path = f'{target}/{filename}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(target_path, 'wb') as fd:
                while chunk := await response.content.read(1024):
                    fd.write(chunk)

    await _count(0, True)

async def _get_urls(flickr, user_id, p, target):
    items = flickr.people.getPublicPhotos(
        user_id=user_id, per_page=500, page=p)['photos']['photo']
    count = len(items)

    for item in items:
        item_id, item_secret = item.get('id'), item.get('secret')
        res = await _get_url(flickr, item_id, item_secret)
        asyncio.create_task(_download(res, target))

    return count

async def _get_url(flickr, item_id, item_secret):
    loop = asyncio.get_event_loop()
    sizes_callback = functools.partial(flickr.photos.getSizes, photo_id=item_id)
    sizes = await loop.run_in_executor(None, sizes_callback)

    sizes = sizes.get('sizes').get('size')
    try:
        original = next(d for d in sizes if d['label'] == 'Original')
        return original.get('source', '')
    except StopIteration:
        return ''
