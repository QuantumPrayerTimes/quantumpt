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

import os

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from prayertimes.ui.wizard.lastpage import LastPage
from prayertimes.ui.wizard.locationofflinepage import LocationOfflinePage
from prayertimes.ui.wizard.locationonlinepage import LocationOnlinePage
from prayertimes.ui.wizard.prayerpage import PrayerPage
from prayertimes.ui.wizard.welcomepage import WelcomeWizardPage

from prayertimes.core.common.logapi import log
from prayertimes.core.common.settings import Settings


class QuantumPTWizard(QtWidgets.QWizard):
    """
    Generic QuantumPT wizard to provide generic functionality and a unified look
    and feel.
    """

    def __init__(self, parent):
        super(QuantumPTWizard, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        # Need to be added, if not, moving frame from a button crash
        self.pressed = 0
        self.offset = self.pos()
        self.was_cancelled = False

        self.finish_button = self.button(QtWidgets.QWizard.WizardButton.FinishButton)
        self.cancel_button = self.button(QtWidgets.QWizard.WizardButton.CancelButton)
        self.next_button = self.button(QtWidgets.QWizard.WizardButton.NextButton)
        self.back_button = self.button(QtWidgets.QWizard.WizardButton.BackButton)
        self.default_button = self.button(QtWidgets.QWizard.WizardButton.CustomButton1)

        self.setup_ui()

        self.welcome_page = WelcomeWizardPage(parent=self)
        self.location_online_page = LocationOnlinePage(parent=self)
        self.location_offline_page = LocationOfflinePage(parent=self)
        self.prayer_page = PrayerPage(parent=self)
        self.last_page = LastPage(parent=self)

        self.welcome_page_id = self.addPage(self.welcome_page)
        self.location_online_page_id = self.addPage(self.location_online_page)
        self.location_offline_page_id = self.addPage(self.location_offline_page)
        self.prayer_page_id = self.addPage(self.prayer_page)
        self.last_page_id = self.addPage(self.last_page)

        self.default_button.clicked.connect(self.on_default_button_clicked)
        self.currentIdChanged.connect(self.on_current_id_changed)

    def setup_ui(self):
        """
        Set up the wizard UI.

        :return:
        """
        self.setObjectName(self.__class__.__name__)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

        self.finish_button.setFixedWidth(100)
        self.cancel_button.setFixedWidth(100)
        self.next_button.setFixedWidth(100)
        self.back_button.setFixedWidth(100)
        self.default_button.setFixedWidth(100)

        button_layout = [
            QtWidgets.QWizard.WizardButton.CustomButton1,
            QtWidgets.QWizard.WizardButton.Stretch,
            QtWidgets.QWizard.WizardButton.BackButton,
            QtWidgets.QWizard.WizardButton.NextButton,
            QtWidgets.QWizard.WizardButton.FinishButton,
            QtWidgets.QWizard.WizardButton.CancelButton,
        ]
        self.setButtonLayout(button_layout)

        self.setModal(True)
        self.setFixedSize(820, 500)

        self.setOptions(
            QtWidgets.QWizard.WizardOption.IndependentPages
            | QtWidgets.QWizard.WizardOption.NoBackButtonOnStartPage
        )

        self.setOption(QtWidgets.QWizard.WizardOption.HaveCustomButton1, True)
        self.setButtonText(QtWidgets.QWizard.WizardButton.CustomButton1, "Default")

        self.setWizardStyle(QtWidgets.QWizard.WizardStyle.ModernStyle)

    def mousePressEvent(self, event):
        self.offset = event.pos()
        self.pressed = 1

    def mouseMoveEvent(self, event):
        if self.pressed:
            x = event.globalPosition().x()
            y = event.globalPosition().y()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(int(x - x_w), int(y - y_w))

    def mouseReleaseEvent(self, event):
        self.pressed = 0

    def showEvent(self, event):
        """
        Center the wizard dialog when appears.

        :param event:
        :return:
        """
        self.move(
            QtWidgets.QApplication.primaryScreen().availableGeometry().center()
            - self.rect().center()
        )
        return super(QuantumPTWizard, self).showEvent(event)

    def exec(self):
        """
        Run the wizard.
        """
        return QtWidgets.QWizard.exec(self)

    def reject(self):
        """
        Stop the wizard on cancel button, close button or ESC key.
        Remove settings file if wizard is not completed.
        """
        log.debug("Wizard cancelled by user.")
        self.was_cancelled = True
        if os.path.exists(Settings().fileName()):
            try:
                os.remove(Settings().fileName())
            except (OSError, FileNotFoundError):
                log.error("File {} not found...".format(Settings().fileName()))
        return super(QuantumPTWizard, self).reject()

    def accept(self):
        """
        The wizard finished correctly.
        Extend settings defined by user by default settings.
        """
        log.debug("Wizard finished. Saving settings ...")
        Settings().extend_current_settings()
        return super(QuantumPTWizard, self).accept()

    def on_current_id_changed(self, page_id):
        """
        Perform necessary functions depending on which wizard page is active.

        :param page_id: current page ID.
        :return:
        """
        if page_id == self.welcome_page_id:
            self.default_button.setDisabled(True)
        elif page_id == self.location_online_page_id:
            self.default_button.setDisabled(True)
        elif page_id == self.location_offline_page_id:
            self.default_button.setDisabled(True)
        elif page_id == self.prayer_page_id:
            self.default_button.setDisabled(False)
        elif page_id == self.last_page_id:
            self.default_button.setDisabled(True)
        elif page_id == -1:
            log.debug("Canceled by user ...")
        else:
            log.error("{} Should never fall here".format("on_current_id_changed"))

    def on_default_button_clicked(self):
        """
        Set default configuration depending on which wizard page is active.

        :return:
        """
        if self.currentId() == self.welcome_page_id:
            pass
        elif self.currentId() == self.location_online_page_id:
            pass
        elif self.currentId() == self.location_offline_page_id:
            pass
        elif self.currentId() == self.prayer_page_id:
            self.prayer_page.set_default_config()
        elif self.currentId() == self.last_page_id:
            pass
        else:
            log.error("{} Should never fall here".format("on_default_button_clicked"))
