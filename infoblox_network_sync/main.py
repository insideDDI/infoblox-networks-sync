"""Sync networks."""

import argparse

from infoblox_client.connector import Connector
from infoblox_client.objects import NetworkV4

from conf.infoblox import Infoblox
from logger import logger


class SyncNetworks:
    return_fields = ["extattrs"]
    attr = {"return_fields": return_fields}

    def __init__(
            self,
            source: Connector,
            destination: Connector):
        self.source = source
        self.destination = destination
        self.execute = False

    @classmethod
    def setUp(
            cls,
            source_hostname: str,
            destination_hostname: str):
        source = Infoblox.connect(source_hostname)
        destination = Infoblox.connect(destination_hostname)

        return cls(source, destination)

    def compare(
            self,
            source_networks: list[NetworkV4],
            destination_networks: list[NetworkV4]):

        src_refs = set([network.ref for network in source_networks])
        dst_refs = set([network.ref for network in destination_networks])

        self._deleted = dst_refs - src_refs
        self._new = src_refs - dst_refs
        logger.info("New networks:")
        logger.info(self._new)
        logger.info("Deleted networks")
        logger.info(self._deleted)

        self._add_networks = [
            n for n in source_networks if n.ref in self._new]
        self._delete_networks = [
            n for n in destination_networks if n.ref in self._deleted]

    def sync_networks(self):

        self.source_networks: list[NetworkV4] = NetworkV4.search_all(
            self.source,
            **self.attr)
        self.destination_networks: list[NetworkV4] = NetworkV4.search_all(
            self.destination,
            **self.attr)[2:]
        self.compare(self.source_networks, self.destination_networks)
        if self.execute:
            logger.info('Writing changes')
            self.save_changes()

    def save_changes(self):
        for network in self._add_networks:
            NetworkV4.create(
                self.destination,
                comment=network.comment,
                network_view=network.network_view,
                network=network.network,
                extattrs=network.extattrs
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Sync networks between infobloxes")
    parser.add_argument("source_hostname")
    parser.add_argument("destination_hostname")
    parser.add_argument("--execute", action='store_true', default=False)
    args = parser.parse_args()
    sync = SyncNetworks.setUp(args.source_hostname, args.destination_hostname)
    sync.execute = args.execute
    sync.sync_networks()
