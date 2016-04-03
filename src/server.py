import aiohttp
from aiohttp import web
import asyncio
import json
import rethinkdb as r

INDEX = open('index.html').read().encode('utf-8')


async def handle(request):
    return web.Response(body=INDEX)


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    feed = await r.table('rand_data').changes().run(app['db'])
    while (await feed.fetch_next()):
        item = await feed.next()
        record = item['new_val']
        record['sampled_at'] = int(record['sampled_at'].timestamp())
        ws.send_str(json.dumps(record))

    return ws


async def set_db(app):
    r.set_loop_type('asyncio')
    app['db'] = await r.connect(host='localhost', port=28015, db="aio")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)

    loop.run_until_complete(set_db(app))
    app.router.add_route('GET', '/', handle)
    app.router.add_route('GET', '/channel', websocket_handler)

    web.run_app(app, port=8888)
