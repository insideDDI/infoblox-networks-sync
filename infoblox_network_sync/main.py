"""Sync networks."""

import argparse

from logger import logger

from networks_sync import SyncNetworks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Sync networks between infobloxes")
    parser.add_argument("source_hostname")
    parser.add_argument("destination_hostname")
    parser.add_argument(
        "--execute",
        action='store_true',
        default=False)
    args = parser.parse_args()
    logger.info(f"Starting sync from {args.source_hostname} to "
                f"{args.destination_hostname}, write mode: "
                f"{args.execute}")
    sync = SyncNetworks.setUp(args.source_hostname, args.destination_hostname)
    sync.execute = args.execute
    sync.sync_networks()
