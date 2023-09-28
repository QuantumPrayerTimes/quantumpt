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

from prayertimes.core.common import de_hump
from prayertimes.core.common.registry import Registry


class RegistryMixin(object):
    """
    This adds registry components to classes to use at run time.
    """

    def __init__(self, parent):
        """
        Register the class and initialization/clean hooks.
        """
        try:
            super(RegistryMixin, self).__init__(parent)
        except TypeError:
            super(RegistryMixin, self).__init__()
        Registry().register_function("__application_init__", self.__application_init__)
        Registry().register_function(
            "__application_post_init__", self.__application_post_init__
        )
        Registry().register_function(
            "__application_clean__", self.__application_clean__
        )

    def __application_init__(self):
        """Override"""
        pass

    def __application_post_init__(self):
        """Override"""
        pass

    def __application_clean__(self):
        """Override"""
        pass


class UniqueRegistryMixin(RegistryMixin):
    """
    This adds a UNIQUE registry components to classes to use at run time.
    """

    def __init__(self, parent):
        """
        Register the unique class.
        """
        try:
            super(UniqueRegistryMixin, self).__init__(parent)
        except TypeError:
            super(UniqueRegistryMixin, self).__init__()
        Registry().register(de_hump(self.__class__.__name__), self)
