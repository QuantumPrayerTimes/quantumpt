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

from PyQt6 import QtWidgets

# from PyQt6.QtGui import QPixmap

from prayertimes.ui.abstract import Dialog


class AboutDialog(Dialog):
    """
    About dialog.
    """

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(
            width=650,
            height=250,
            obj_name=self.__class__.__name__,
            titlebar_name="About",
            titlebar_icon=None,
            parent=parent,
        )

        grid_layout = QtWidgets.QGridLayout()

        self.name_prog = QtWidgets.QLabel("QuantumPrayerTimes", self)

        self.label_version = QtWidgets.QLabel("v0.0.1", self)
        self.label_copyright = QtWidgets.QLabel(
            "Copyright 2017 QuantumPrayerTimes", self
        )
        self.label_contribution = QtWidgets.QLabel(
            "Special thanks to all people for contribution.", self
        )

        grid_layout.addWidget(self.name_prog, 0, 0)
        grid_layout.addWidget(self.label_version, 1, 0)
        grid_layout.addWidget(self.label_copyright, 2, 0)
        grid_layout.addWidget(self.label_contribution, 0, 1, 3, 1)

        self.dialog_frame.setLayout(grid_layout)
