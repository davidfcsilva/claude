import asyncio
from fleet import FleetRouter, load_config

router = FleetRouter(load_config())

async def main():
    answer = await router.ask("solve 5x - 3 = 12")
    print(answer)
    await router.aclose()  # closes the aiohttp pool — silences warnings

asyncio.run(main())