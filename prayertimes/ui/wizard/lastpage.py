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
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class LastPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(LastPage, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout()

        self.icon = QtWidgets.QLabel(self)
        self.icon.setPixmap(QPixmap(":/icons/wizard_set.png"))
        self.icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

        self.title_label = QtWidgets.QLabel("You're all set !\n", self)
        self.title_label.setStyleSheet(
            "QLabel {color: #6F8DA6; font: 60px 'capsuula';}"
        )
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

        self.layout.addStretch()
        self.layout.addWidget(self.icon)
        self.layout.addStretch()
        self.layout.addWidget(self.title_label)

        self.setLayout(self.layout)
