import json
import logging
import asyncio
from contextlib import contextmanager

import aiocsv
import aiohttp
import aiofiles

try:
    # noinspection PyUnresolvedReferences
    import uvloop

except ImportError:
    pass

else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

try:
    from config import (
        DAEMON_RPC_HOST,
        DAEMON_RPC_PORT,
        DAEMON_RPC_SSL,
        OUTPUT_FILE_NAME,
    )

except ImportError:
    DAEMON_RPC_HOST = "localhost"
    DAEMON_RPC_PORT = 6969
    DAEMON_RPC_SSL = False
    OUTPUT_FILE_NAME = "checkpoints.csv"

DAEMON_RPC_URL = (
    f"http{'s' if DAEMON_RPC_SSL else ''}://{DAEMON_RPC_HOST}:{DAEMON_RPC_PORT}"
)


@contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        handler = logging.StreamHandler()

        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        log.addHandler(handler)
        log.setLevel(logging.INFO)

        yield

    finally:
        handlers = log.handlers[:]

        for _handler in handlers:
            _handler.close()
            log.removeHandler(_handler)


async def _make_get_request(method: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{DAEMON_RPC_URL}/{method}") as res:
            return await res.json()


async def _make_post_request(method: str, **kwargs) -> dict:
    headers = {"Content-Type": "application/json"}

    params = {
        "jsonrpc": "2.0",
        "method": method,
        "params": kwargs,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{DAEMON_RPC_URL}/json_rpc",
            headers=headers,
            data=json.dumps(params),
        ) as res:
            return await res.json()


async def get_height() -> int:
    return (await _make_get_request("info"))["height"]


async def get_block_hash_by_height(height: int) -> dict:
    params = {
        "height": height,
    }

    return (await _make_post_request("getblockheaderbyheight", **params))["result"][
        "block_header"
    ]["hash"]


async def generate_checkpoints() -> None:
    log = logging.getLogger()
    log.info("Generating checkpoints...")

    current_height = await get_height()
    log.info(f"Current height: {current_height}")

    async with aiofiles.open(OUTPUT_FILE_NAME, "w", encoding="utf-8", newline="") as f:
        writer = aiocsv.AsyncWriter(f)

        for height in range(0, current_height):
            block_hash = await get_block_hash_by_height(height)
            await writer.writerow([height, block_hash])
            log.info(f"Generated checkpoint for height {height}")

    log.info(f"Checkpoints generated and saved to {OUTPUT_FILE_NAME}")


async def main() -> None:
    with setup_logging():
        await generate_checkpoints()


if __name__ == "__main__":
    asyncio.run(main())
