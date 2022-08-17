import asyncio
from pprint import pprint

from vigobus import Vigobus


async def main():
    v = Vigobus()
    print(v._datasources)
    pprint((await v.get_stop(420)).dict())
    pprint((await v.get_buses(5800)).dict())

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
