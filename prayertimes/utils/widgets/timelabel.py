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
from PyQt6.QtCore import QTime, QTimer


class TimeLabel(QtWidgets.QLabel):
    """
    Simple label that prints time.
    """

    def __init__(self, parent=None):
        super(TimeLabel, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.__display_time)
        self.timer.start()

        self.__display_time()

    def __display_time(self):
        self.setText(QTime.currentTime().toString())
