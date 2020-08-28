"""
:mod:`config` -- reading configuration files
============================================

.. module:: config
    :synopsis: Provides functions for manipulating configuration files
               e.g. reading setting from a configuration file.

"""
import inspect
import os.path
from configparser import RawConfigParser


class _ConfigParser(RawConfigParser):
    def __init__(self):
        RawConfigParser.__init__(self)
        self.readonce = False
        self.config_file = self._get_default_config()
        if os.path.exists(self.config_file):
            self._read_file()

    def _get_default_config(self):
        cmd_folder = os.path.realpath(
            os.path.abspath(
                os.path.split(
                    inspect.getfile(
                        inspect.currentframe()))[0]))
        par_folder = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        file_path = os.path.join(par_folder, 'multiplier_conf.cfg')
        return file_path

    def _read_file(self):
        if not self.readonce:
            self.read(self.config_file)
            self.readonce = True

    def set_config_file(self, config_file):
        self.config_file = config_file
        self.readonce = False
        self._read_file()


configparser = _ConfigParser()
