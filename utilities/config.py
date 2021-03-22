"""
:mod:`config` -- reading configuration files
============================================

.. module:: config
    :synopsis: Provides functions for manipulating configuration files
               e.g. reading and setting from a configuration file.
               It provides better control in unit testing to override
               config file and values.

"""
import inspect
import os.path
from configparser import RawConfigParser


def _get_default_config():
    """
    Calculates default configuration file path if no file
    location is provided. It defaults to multiplier_conf.cfg
    inside project root directory
    """
    cmd_folder = os.path.realpath(
        os.path.abspath(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()))[0]))
    par_folder = os.path.abspath(os.path.join(cmd_folder, os.pardir))
    return os.path.join(par_folder, 'multiplier_conf.cfg')


class _ConfigParser(RawConfigParser):
    def __init__(self):
        RawConfigParser.__init__(self)
        self.readonce = False
        self.config_file = _get_default_config()
        if os.path.exists(self.config_file):
            self._read_file()

    def _read_file(self):
        """
        Read the specified config file if not read already
        """
        if not self.readonce:
            self.read(self.config_file)
            self.readonce = True

    def set_config_file(self, config_file):
        """
        Change configuration file
        """
        self.config_file = config_file
        self.readonce = False
        self._read_file()


configparser = _ConfigParser()
