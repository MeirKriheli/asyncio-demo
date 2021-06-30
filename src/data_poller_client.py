from datetime import datetime
import asyncio
import aiohttp
import rethinkdb as rdb
import pytz

RANDOM_URL = 'http://localhost:8888/random'


async def fetch_data(session, url, r, connection):
    while True:
        async with session.get(url) as response:
            assert response.status == 200
            value = await response.read()
            int_value = int(value, 16)
            print('Got value %d' % int_value)
            doc = {'sampled_at': datetime.now(pytz.utc), 'value': int_value}
            await r.table('rand_data').insert(doc).run(connection)
            await asyncio.sleep(0.5)


async def main(loop):
    r = rdb.RethinkDB()
    r.set_loop_type('asyncio')
    connection = await r.connect(host='localhost', port=49157, db="aio")

    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(loop=loop, timeout=timeout) as session:
        await fetch_data(session, RANDOM_URL, r, connection)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
