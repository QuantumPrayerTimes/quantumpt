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

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from prayertimes.core.common.settings import Settings
from prayertimes.core.lib.prayer.prayertimes import PrayTimes

from prayertimes.ui.abstract import CheckableButton


class SimplestLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(SimplestLabel, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.setWordWrap(True)


class MethodFrame(QtWidgets.QFrame):
    method_dict = PrayTimes.methods
    default_method = 'MWL'

    def __init__(self, parent=None):
        super(MethodFrame, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(10)
        self.method_button_layout = QtWidgets.QHBoxLayout()

        self.question_label = QtWidgets.QLabel("Please select your calculation method :")

        self.label = SimplestLabel(self)
        self.group = QtWidgets.QButtonGroup()

        for method in PrayTimes.method_list:
            btn = CheckableButton(method)
            btn.clicked.connect(self._toggle_button)
            self.group.addButton(btn)

            self.method_button_layout.addWidget(btn)

        self.layout.addWidget(self.question_label)
        self.layout.addLayout(self.method_button_layout)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def _toggle_button(self):
        """
        Select the correct method depending on which button has been selected.

        :return:
        """
        # Get method name reading button text
        method = self.sender().text()
        method_name = self.method_dict[method]['name']
        method_region = self.method_dict[method]['region']

        Settings().setValue("prayer_settings/calculation", method)
        self.label.setText("{} used commonly in {}".format(method_name, method_region))

    def set_default(self, method=default_method):
        """
        Set default method to <MWL> which is the common method used in most countries.

        :param method: default method that should be used for calculation prayer.
        :return:
        """
        for btn in self.group.buttons():
            if btn.text() == method:
                btn.setChecked(True)
                btn.clicked.emit()


class AsrSettingsFrame(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(AsrSettingsFrame, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(10)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.question_label = QtWidgets.QLabel("Please select your asr setting method :")

        self.asr_method_label = SimplestLabel(self)
        self.group = QtWidgets.QButtonGroup()

        self.standard_btn = CheckableButton("Standard")
        self.standard_btn.clicked.connect(self.asr_method_selected)

        self.hanafi_btn = CheckableButton("Hanafi")
        self.hanafi_btn.clicked.connect(self.asr_method_selected)

        self.group.addButton(self.standard_btn)
        self.group.addButton(self.hanafi_btn)

        self.h_layout.addWidget(self.standard_btn)
        self.h_layout.addWidget(self.hanafi_btn)
        self.h_layout.addWidget(self.asr_method_label)

        self.layout.addWidget(self.question_label)
        self.layout.addLayout(self.h_layout)

        self.setLayout(self.layout)

    def asr_method_selected(self):
        """
        Select the correct asr settings depending on which button has been selected.

        :return:
        """
        if self.hanafi_btn.isChecked():
            self.asr_method_label.setText("Hanafi")
            Settings().setValue("prayer_settings/asr_method", "Hanafi")
        else:
            self.asr_method_label.setText("Standard (Imams Shafi'i, Hanbali et Maliki)")
            Settings().setValue("prayer_settings/asr_method", "Standard")

    def set_default(self):
        """
        Set default method to <Standard> which is the common asr settings used in most countries.

        :return:
        """
        # Set the default value to standard method
        self.standard_btn.setChecked(True)
        self.hanafi_btn.setChecked(False)
        self.asr_method_label.setText("Standard (Imams Shafi'i, Hanbali et Maliki)")
        Settings().setValue("prayer_settings/asr_method", "Standard")


class PrayerPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(PrayerPage, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.method_frame = MethodFrame(parent=self)
        self.asr_frame = AsrSettingsFrame(parent=self)

        self.setTitle("Prayer Settings Platform")
        self.setSubTitle("\nPrayer settings permits to determine which calculation method is the most appropriate to "
                         "your location.\n\nUnder each method, you can find a quick overview which explain where the "
                         "method is based and the most approriate location.")
        self.setPixmap(QtWidgets.QWizard.BannerPixmap, QPixmap(":/icons/wizard_prayer.png"))

        self.layout.addWidget(self.method_frame)
        self.layout.addWidget(self.asr_frame)

        self.setLayout(self.layout)

    def initializePage(self):
        """
        Init page with default methods.

        :return:
        """
        self.method_frame.set_default()
        self.asr_frame.set_default()
        return super(PrayerPage, self).initializePage()

    def set_default_config(self):
        """
        Set default configurations for method and asr settings.

        :return:
        """
        self.asr_frame.set_default()
        self.method_frame.set_default()
