__version__ = "1.0.5b"

import json
from typing import Optional, AnyStr
import logging
import asyncio
from contextlib import contextmanager

import asyncclick as click
import aiocsv
import aiohttp
import aiofiles
from dotenv import dotenv_values

try:
    # noinspection PyUnresolvedReferences
    import uvloop

except ImportError:
    pass

else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

DEFAULT_DAEMON_RPC_HOST: str = "localhost"
DEFAULT_DAEMON_RPC_PORT: int = 6969
DEFAULT_DAEMON_RPC_SSL: str = "False"
DEFAULT_OUTPUT_FILE_NAME: str = "checkpoints.csv"

OUTPUT_FILE_NAME: str = AnyStr
DAEMON_RPC_URL: str = AnyStr


def load_from_env():
    config: dict = dotenv_values(".env")

    return (
        config.get("DAEMON_RPC_HOST", DEFAULT_DAEMON_RPC_HOST),
        int(config.get("DAEMON_RPC_PORT", DEFAULT_DAEMON_RPC_PORT)),
        config.get("DAEMON_RPC_SSL", DEFAULT_DAEMON_RPC_SSL).lower()
        in ("true", "1"),
        config.get("OUTPUT_FILE_NAME", DEFAULT_OUTPUT_FILE_NAME),
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


async def generate_checkpoints(check_existing: Optional[bool] = False) -> None:
    log = logging.getLogger()

    if check_existing:
        try:
            log.info("Checking for existing checkpoints...")
            async with aiofiles.open(
                OUTPUT_FILE_NAME, "r", encoding="utf-8", newline=""
            ) as f:
                entry = (await f.readlines())[-1]
                height, _ = entry.split(",")
                height = int(height)

                log.info(f"Checkpoints found. Last checkpoint: {height}")

        except FileNotFoundError:
            log.info("No existing checkpoints found.")

        except Exception as e:
            log.exception(
                f"An error occurred while checking for existing checkpoints: {e}"
            )

    log.info("Generating checkpoints...")

    try:
        current_height = await get_height()
        log.info(f"Current height: {current_height}")

        if "height" in locals() and height < current_height:
            start_height = height
            log.info(f"Resuming from height {start_height}")

        else:
            start_height = 0

        async with aiofiles.open(
            OUTPUT_FILE_NAME, "a", encoding="utf-8", newline=""
        ) as f:
            writer = aiocsv.AsyncWriter(f)

            for height in range(start_height, current_height):
                block_hash = await get_block_hash_by_height(height)
                await writer.writerow([height, block_hash])
                log.info(f"Generated checkpoint for height {height}")

        log.info(f"Checkpoints generated and saved to {OUTPUT_FILE_NAME}")

    except aiohttp.client_exceptions.ClientConnectorError:
        log.exception("Could not connect to the daemon RPC. Exiting...")
        log.info("Check if the DeroGold daemon is running and run the script again.")
        log.info(f"Progress has been saved to {OUTPUT_FILE_NAME}.")


@click.command()
@click.option("--version", is_flag=True, help="Show the version and exit")
@click.option(
    "--check-existing", is_flag=True, help="Check for existing checkpoints"
)
@click.option(
    "--daemon-rpc-host",
    type=click.STRING,
    help="Daemon RPC host address (e.g. localhost)",
)
@click.option(
    "--daemon-rpc-port", type=click.INT, help="Daemon RPC port (usually 6969)"
)
@click.option("--daemon-rpc-ssl", is_flag=True, help="Use SSL for daemon RPC")
@click.option(
    "--output-file-name",
    type=click.STRING,
    help="Output file name (e.g. checkpoints.csv)",
)
async def main(
    version: bool,
    check_existing: bool,
    daemon_rpc_host: str,
    daemon_rpc_port: int,
    daemon_rpc_ssl: bool,
    output_file_name: str,
) -> None:
    """
    A python script to generate checkpoints for the DeroGold blockchain.

    This script is authored by Sayan "Sn1F3rt" Bhattacharyya and is licensed under the MIT License.

    """
    if version:
        click.echo(f"DeroGold Checkpoints Generator v{__version__}")
        return

    with setup_logging():
        _daemon_rpc_host, _daemon_rpc_port, _daemon_rpc_ssl, _output_file_name = (
            load_from_env()
        )

        daemon_rpc_host = daemon_rpc_host or _daemon_rpc_host
        daemon_rpc_port = daemon_rpc_port or _daemon_rpc_port
        daemon_rpc_ssl = daemon_rpc_ssl or _daemon_rpc_ssl

        global OUTPUT_FILE_NAME, DAEMON_RPC_URL

        OUTPUT_FILE_NAME = output_file_name or _output_file_name
        DAEMON_RPC_URL = f"http{'s' if daemon_rpc_ssl else ''}://{daemon_rpc_host}:{daemon_rpc_port}"

        await generate_checkpoints(check_existing)


if __name__ == "__main__":
    asyncio.run(main())
