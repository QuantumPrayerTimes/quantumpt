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
from PyQt6.QtCore import Qt

from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registrymixin import UniqueRegistryMixin

from prayertimes.ui.mainframe import MainFrame
from prayertimes.ui.mainframeselector import MainFrameSelector


class PrincipalFrame(UniqueRegistryMixin, QtWidgets.QFrame):
    """
    Principal Frame that contains all widgets and the frame that selects between widgets.
    """

    def __init__(self, parent=None):
        super(PrincipalFrame, self).__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setObjectName(self.__class__.__name__)

        self.container_stack = QtWidgets.QStackedWidget(self)

        self.main_frame_selector = MainFrameSelector(self)

        self.main_frame = MainFrame(self)

        self.container_stack.addWidget(self.main_frame)

        # Set margin between frame and borders
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Set margin between elements of layout
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

        self.layout.addWidget(self.container_stack)
        self.layout.addWidget(self.main_frame_selector)

        Registry().register_function("set_main_stack", self.set_stack)

    def __application_init__(self):
        # Set first time to main frame
        self.set_stack(0)
        pass

    def __application_clean__(self):
        pass

    def set_stack(self, idx):
        """
        Set the visible widget to widget at index <idx>

        :param idx: index of the widget to be visible.
        :return:
        """
        self.container_stack.setCurrentIndex(idx)
        self.main_frame_selector.listwidget_frame.setCurrentRow(idx)
