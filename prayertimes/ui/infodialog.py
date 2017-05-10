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

# import os
#
# from PyQt5 import QtWidgets
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import Qt

from prayertimes.ui.abstract import Dialog


class InfoDialog(Dialog):
    """
    About dialog.
    """

    def __init__(self, parent=None):
        super(InfoDialog, self).__init__(width=650, height=290, obj_name="AboutDialog",
                                         titlebar_name="Info", titlebar_icon=None, parent=parent)

