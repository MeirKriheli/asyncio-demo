import asyncio
import json
import random

import aiohttp
from aiohttp import web
import rethinkdb as rdb

INDEX = open('index.html').read().encode('utf-8')

async def random_val(request):
    val = random.randint(1000, 8000)
    return web.Response(text=f'{val:x}')

async def handle(request):
    return web.Response(body=INDEX, content_type='text/html')


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    r = app['r']
    feed = await r.table('rand_data').changes().run(app['db'])
    while await feed.fetch_next():
        item = await feed.next()
        record = item['new_val']
        record['sampled_at'] = int(record['sampled_at'].timestamp())
        await ws.send_str(json.dumps(record))

    return ws


async def set_db(app):
    r = rdb.RethinkDB()
    r.set_loop_type('asyncio')
    app['db'] = await r.connect(host='localhost', port=49157, db="aio")
    app['r'] = r


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)

    loop.run_until_complete(set_db(app))
    app.router.add_route('GET', '/', handle)
    app.router.add_route('GET', '/channel', websocket_handler)
    app.router.add_route('GET', '/random', random_val)

    web.run_app(app, port=8888)
