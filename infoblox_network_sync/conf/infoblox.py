"""Infoblox backend connector."""

from infoblox_client import connector

from .conftool import Config, ConfigWrapper
from logger import logger


class Infoblox:
    """Infoblox object."""

    @staticmethod
    def login(filename: str) -> dict[str, str]:
        """Return login credentials.

        Parameters
        ----------
        hostname: Hostname

        Returns
        -------
        Login credentials
        """
        cnf: Config
        cnf = ConfigWrapper.read(filename)

        logger.debug(f'Retrieved secrets from {filename}: secrets')
        return {
            'host': cnf.hostname,
            'username': cnf.username,
            'password': cnf.password,
            'wapi_version': cnf.api_version,
            'ssl_verify': cnf.ssl_validate
        }

    @staticmethod
    def connect(hostname: str) -> connector.Connector:
        """Return connector object."""
        opts: dict[str, str]
        opts = Infoblox.login(f'{hostname}.yaml')
        return connector.Connector(opts)
