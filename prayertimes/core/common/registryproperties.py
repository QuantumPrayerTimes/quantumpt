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

from prayertimes.core.common.registry import Registry
from prayertimes.core.common import is_win


class RegistryProperties(object):
    """
    This adds registry components to classes to use at run time.
    """

    @property
    def application(self):
        """
        Adds the praypertimes to the class dynamically.
        Windows needs to access the application in a dynamic manner.
        """
        if is_win():
            return Registry().get("application")
        else:
            if not hasattr(self, "_application") or not self._application:
                self._application = Registry().get("application")
            return self._application

    @property
    def global_frame(self):
        """
        Adds the global_frame to the class dynamically.
        """
        if not hasattr(self, "_global_frame") or not self._global_frame:
            self._global_frame = Registry().get("global_frame")
        return self._global_frame

    @property
    def prayer_frame(self):
        """
        Adds the prayers container frame to the class dynamically.
        """
        if (
            not hasattr(self, "_prayers_container_frame")
            or not self._prayers_container_frame
        ):
            self._prayers_container_frame = Registry().get("prayers_container_frame")
        return self._prayers_container_frame

    @property
    def media_manager(self):
        """
        Adds the media manager to the class dynamically.
        """
        if not hasattr(self, "_media_manager") or not self._media_manager:
            self._media_manager = Registry().get("media_manager")
        return self._media_manager

    @property
    def prayer_manager(self):
        """
        Adds the prayer manager to the class dynamically.
        """
        if not hasattr(self, "_prayer_manager") or not self._prayer_manager:
            self._prayer_manager = Registry().get("prayer_manager")
        return self._prayer_manager

    @property
    def scheduler_manager(self):
        """
        Adds the scheduler manager to the class dynamically.
        """
        if not hasattr(self, "_scheduler_manager") or not self._scheduler_manager:
            self._scheduler_manager = Registry().get("scheduler_manager")
        return self._scheduler_manager
