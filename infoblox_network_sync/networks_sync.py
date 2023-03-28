"""Network sync class."""
from typing import Tuple

from infoblox_client.connector import Connector
from infoblox_client.objects import NetworkV4

from conf.infoblox import Infoblox
from logger import logger


class SyncNetworks:
    """Network objects sync wrapper.
    """
    return_fields = ["extattrs"]
    attr = {
        "return_fields": return_fields,
        "paging": True
    }

    def __init__(
            self,
            source: Connector,
            destination: Connector):
        """Instantiate wrapper instance.

        Parameters
        ----------
        source: connector for synchronization source
        destination: connector for synchronization destination
        """
        self.source = source
        self.destination = destination
        self.execute = False

    @classmethod
    def setUp(
            cls,
            source_hostname: str,
            destination_hostname: str) -> Tuple(Connector, Connector):
        """Helper method to establish connectors.

        Parameters
        ----------
        source_hostname: hostname of the source appliance
        destination_hostname: hostname of the destination appliance

        Returns
        -------
        Source/destination connectors pair
        """
        source = Infoblox.connect(source_hostname)
        destination = Infoblox.connect(destination_hostname)

        return cls(source, destination)

    def compare(
            self,
            source_networks: list[NetworkV4],
            destination_networks: list[NetworkV4]):
        """Compare source and destination network objects.

        Parameters
        ----------
        source_networks: desired networks state in source appliance
        destination_networks: actual destination networks state

        Returns
        -------

        """

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
        """Automation wrapper."""

        self.source_networks: list[NetworkV4] = NetworkV4.search_all(
            self.source,
            **self.attr)
        self.destination_networks: list[NetworkV4] = NetworkV4.search_all(
            self.destination,
            **self.attr)
        self.compare(self.source_networks, self.destination_networks)
        if self.execute:
            logger.info('Writing changes')
            self.create_networks()

    def create_networks(self):
        for network in self._add_networks:
            NetworkV4.create(
                self.destination,
                comment=network.comment,
                network_view=network.network_view,
                network=network.network,
                extattrs=network.extattrs
            )
