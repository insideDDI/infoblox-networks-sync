"""Configuration for connectors from config file."""

import inquirer as iq
import yaml

from pydantic import BaseSettings
from logger import logger
from os import mkdir
from os.path import exists
from os.path import join as pjoin

BASEDIR = 'hosts'


class Config(BaseSettings):
    """Config object."""

    username: str
    password: str
    hostname: str
    api_version: str = ""
    ssl_validate: bool = True


class ConfigWrapper:
    """Read config from file."""

    @staticmethod
    def read(filename: str) -> Config:
        """Read config file."""
        fpath = pjoin(BASEDIR, filename)
        if not exists(fpath):
            ConfigWrapper.create()
        try:
            with open(fpath) as infile:
                data = yaml.safe_load(infile.read())
        except Exception as e:
            print(f'Error reading data: {e}')

        return Config(**data)

    @staticmethod
    def create():
        """Create empty config file."""
        if not exists('hosts'):
            logger.debug(f'creating <{BASEDIR}> directory')
            mkdir(f'{BASEDIR}')
        questions = [
            iq.Text('hostname', message="hostname"),
            iq.Text('username', message="username"),
            iq.Password('password', message="password"),
            iq.Text('api_version', message="API version", default="2.12.2"),
            iq.Confirm('ssl_validate', message='validate SSL', default=False)
            ]
        responses = iq.prompt(questions)
        fname_base = responses['hostname']
        with open(f'{BASEDIR}/{fname_base}.yaml', 'w') as outf:
            outf.write(yaml.safe_dump(responses))
            logger.debug(f'config saved to {BASEDIR}/{fname_base}.yaml')
