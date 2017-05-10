#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------- #
# QuantumPT - Open Source Portable Islamic prayer times reminder              #
# --------------------------------------------------------------------------- #
# Copyright (c) 2016 QuantumPT Developer                                      #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 3 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
# --------------------------------------------------------------------------- #
# Some functions present in this file has been originally used in OpenLP      #
# project : https://openlp.org                                                #
# --------------------------------------------------------------------------- #

from PyQt5.QtCore import QDir

# Use current dir because application is run from quantum.py
# When application is compiled and deployed, the src_folder
# is always considered as the root directory from which the
# executable is run.
src_root_dir = QDir().currentPath()


class ResourcesLocation(object):
    """
    The ResourcesLocation class is a static class which retrieves the absolute directory path
    based on the directory type.
    """
    __AppDir__ = 1
    __ResourcesDir__ = 2
    __AthanDir__ = 3
    __DuaDir__ = 4
    __LanguageDir__ = 5
    __IconsDir__ = 6
    __ImagesDir__ = 7
    __DatabaseDir__ = 8
    __FontDir__ = 9
    __LogsDir__ = 10

    @staticmethod
    def get_directory(dir_type=__AppDir__):
        """
        :param dir_type: The directory type you want, for instance the data directory.
                         Default *ResourcesLocation.AppDir*

        :return: The appropriate directory according to the directory type.
        """
        if dir_type == ResourcesLocation.__AppDir__:
            return src_root_dir

        elif dir_type == ResourcesLocation.__ResourcesDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path

        elif dir_type == ResourcesLocation.__AthanDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'athans'

        elif dir_type == ResourcesLocation.__DuaDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'duas'

        elif dir_type == ResourcesLocation.__LanguageDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'i18n'

        elif dir_type == ResourcesLocation.__IconsDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'icons'

        elif dir_type == ResourcesLocation.__ImagesDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'images'

        elif dir_type == ResourcesLocation.__DatabaseDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'database'

        elif dir_type == ResourcesLocation.__FontDir__:
            app_path = _get_os_dir_path(dir_type)
            return app_path + 'fonts'

        elif dir_type == ResourcesLocation.__LogsDir__:
            return src_root_dir + '/logs'

        else:
            return _get_os_dir_path(dir_type)

    @property
    def root_dir(self):
        return self.get_directory(ResourcesLocation.__AppDir__)

    @property
    def resources_dir(self):
        return self.get_directory(ResourcesLocation.__ResourcesDir__)

    @property
    def athan_dir(self):
        return self.get_directory(ResourcesLocation.__AthanDir__)

    @property
    def dua_dir(self):
        return self.get_directory(ResourcesLocation.__DuaDir__)

    @property
    def language_dir(self):
        return self.get_directory(ResourcesLocation.__LanguageDir__)

    @property
    def icons_dir(self):
        return self.get_directory(ResourcesLocation.__IconsDir__)

    @property
    def images_dir(self):
        return self.get_directory(ResourcesLocation.__ImagesDir__)

    @property
    def database_dir(self):
        return self.get_directory(ResourcesLocation.__DatabaseDir__)

    @property
    def font_dir(self):
        return self.get_directory(ResourcesLocation.__FontDir__)

    @property
    def logs_dir(self):
        return self.get_directory(ResourcesLocation.__LogsDir__)


def _get_os_dir_path(dir_type):
    """
    :param dir_type: The directory type you want, for instance the data directory.
    :return: A absolute path.
    """
    if dir_type == ResourcesLocation.__AthanDir__ or dir_type == ResourcesLocation.__DuaDir__:
        directory = src_root_dir + '/resources/multimedia/'
        if QDir().exists(directory):
            return directory
    else:
        directory = src_root_dir + '/resources/'
        if QDir().exists(directory):
            return directory
