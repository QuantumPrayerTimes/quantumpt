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

import time

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap


class SplashScreen(QtWidgets.QSplashScreen):
    """
    Class implementing a splashscreen.
    """

    start_splashscreen = pyqtSignal()
    splash_time = 50

    def __init__(self, parent=None):
        super(SplashScreen, self).__init__(parent)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setObjectName(self.__class__.__name__)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        pixmap = QPixmap(":/images/splashscreen.png")
        self.setPixmap(pixmap)
        self.setMask(pixmap.mask())

        self.start_splashscreen.connect(self.fade_opacity)

    def fade_opacity(self):
        """
        Fade splashscreen until it is visible.

        :return:
        """
        self.setWindowOpacity(0)
        t = 0
        while t <= self.splash_time:
            _opacity = self.windowOpacity() + 1 / self.splash_time
            if _opacity > 1:
                break
            self.setWindowOpacity(_opacity)
            self.show()
            t += 1
            time.sleep(0.5 * (1 / self.splash_time))

    def finish(self, widget):
        t = 0
        while t <= self.splash_time:
            _opacity = self.windowOpacity() - 1 / self.splash_time
            if _opacity < 0:
                self.close()
                break
            self.setWindowOpacity(_opacity)
            self.show()
            t += 1
            time.sleep(0.5 * (1 / self.splash_time))

        return QtWidgets.QSplashScreen().finish(widget)
