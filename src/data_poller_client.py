from datetime import datetime
import asyncio
import aiohttp
import rethinkdb as r
import pytz

RANDOM_URL = 'http://dev-random-as-a-service.appspot.com/dev/urandom?count=2'


async def fetch_data(session, url, connection_future):
    connection = await connection_future
    while True:
        with aiohttp.Timeout(20):
            async with session.get(url) as response:
                assert response.status == 200
                value = await response.read()
                int_value = int(value, 16)
                print('Got value %d' % int_value)
                doc = {'sampled_at': datetime.now(pytz.utc), 'value': int_value}
                await r.table('rand_data').insert(doc).run(connection)
                await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    r.set_loop_type('asyncio')
    connection = r.connect(host='localhost', port=28015, db="aio")

    with aiohttp.ClientSession(loop=loop) as session:
        asyncio.async(fetch_data(session, RANDOM_URL, connection))
        loop.run_forever()
