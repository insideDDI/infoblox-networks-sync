"""Network sync class."""
from typing import TypeVar

from infoblox_client.connector import Connector
from infoblox_client.objects import NetworkV4, EADefinition

from conf.infoblox import Infoblox
from logger import logger

T = TypeVar("T", bound="SyncNetworks")


class SyncNetworks:
    """Network objects sync wrapper."""

    return_fields = ["extattrs", "comment", "network_view", "network"]
    attr = {
        "return_fields": return_fields,
        "paging": True
    }

    ea_return_fields = ["comment", "name", "type", "flags",
            "default_value", "list_values", "namespace"]
    ea_attr = {
        "return_fields": ea_return_fields,
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
        # self.ea_def_source = ea_def_source
        # self.ea_def_destination = ea_def_destination
        self.execute = False

    @classmethod
    def setUp(
            cls: type[T],
            source_hostname: str,
            destination_hostname: str) -> T:
        """Instantiate class based on hostnames.

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
        """
        src_refs = set([network.ref for network in source_networks])
        dst_refs = set([network.ref for network in destination_networks])

        logger.info(source_networks)
        logger.info(destination_networks)

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


    def compare_ea(
            self,
            source_eas: list[EADefinition],
            destination_eas: list[EADefinition]):
        """Compare source and destination EA definition objects.

        Parameters
        ----------
        source_networks: desired EAs state in source appliance
        destination_networks: actual destination EAs state
        """
        src_ea_refs = set([ea.ref for ea in source_eas])
        dst_ea_refs = set([ea.ref for ea in destination_eas])

        logger.info(source_eas)
        logger.info(destination_eas)

        self._deleted_eas = dst_ea_refs - src_ea_refs
        self._new_eas = src_ea_refs - dst_ea_refs
        logger.info("New networks:")
        logger.info(self._new_eas)
        logger.info("Deleted networks")
        logger.info(self._deleted_eas)

        self._add_eas = [
            e for e in source_eas if e.ref in self._new_eas]
        self._delete_eas = [
            e for e in destination_eas if e.ref in self._deleted_eas]

    def sync_networks(self):
        """Automation wrapper."""
        self.source_networks: list[NetworkV4] = NetworkV4.search_all(
            self.source,
            **self.attr)
        self.destination_networks: list[NetworkV4] = NetworkV4.search_all(
            self.destination,
            **self.attr)
        self.ea_def_source: list[EADefinition] = EADefinition.search_all(
            self.source,
            **self.ea_attr
            )
        self.ea_def_destination: list[EADefinition] = EADefinition.search_all(
            self.destination,
            **self.ea_attr
            )
        logger.info(self.ea_def_source)
        logger.info(self.ea_def_destination)

        self.compare(self.source_networks, self.destination_networks)
        self.compare_ea(self.ea_def_source, self.ea_def_destination)
        if self.execute:
            logger.info('Writing changes')
            self.create_eas()
            self.create_networks()
            self.delete_networks()
            # self.create_eas()

    def create_networks(self):
        """Create networks not present in the destination appliance DB."""
        for network in self._add_networks:
            # for network in self._add_networks:
            logger.info(f"NETWORK IN CREATION: {network}")
            msg = NetworkV4.create(
                self.destination,
                comment=network.comment,
                network_view=network.network_view,
                network=network.network,
                extattrs=network.extattrs
            )

    def delete_networks(self):
        for network in self._delete_networks:
            logger.info(f"Delete: {network.ref}")
            self.destination.delete_object(network.ref) 

    def create_eas(self):
        """Create EAs not present in the destination appliance DB."""
        for ea in self._add_eas:
            logger.info(f"EAS PRZEMEK: {ea}")
            ["comment", "name", "type",
            "default_value"]
            msg = EADefinition.create(
                self.destination,
                comment=ea.comment,
                name=ea.name,
                type=ea.type,
                flags=ea.flags,
                list_values=ea.list_values,
                default_value=ea.default_value,
            )
            logger.info(msg)

# TODO network_views = conn.get_object('networkview')
# TODO returned_fields to be checked for network/EA/NetViews
#
