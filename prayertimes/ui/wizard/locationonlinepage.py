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
from PyQt5.QtGui import QPixmap, QFont

from prayertimes.core.common.logapi import log
from prayertimes.core.common.resourceslocation import ResourcesLocation
from prayertimes.core.common.settings import Settings

from prayertimes.ui.abstract import TaskThread, FrameCitySetting

from prayertimes.utils.city_infos import City
from prayertimes.utils.ip_location import connected_to_internet, get_public_ip, get_location_from_ip
from prayertimes.utils.widgets.waitoverlay import WaitingOverlay


class OnlineFrameWizard(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super(OnlineFrameWizard, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.located = False
        self.initialized = False

        self.layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()

        self.overlay = WaitingOverlay(self)
        self.overlay.hide()

        self.not_connected_label = QtWidgets.QLabel("Cannot detect location using internet..  :(\n"
                                                    "Please proceed to setup your city",
                                                    self)
        self.not_connected_label.setFont(QFont("capsuula", 30))
        self.not_connected_label.hide()

        self.retry_connection_btn = QtWidgets.QPushButton('Retry to connect', self)
        self.go_offline_radio = QtWidgets.QRadioButton('Not your city ? '
                                                       'Check it to select your city manually', self)
        self.go_offline_radio.hide()

        self.frame_city = FrameCitySetting(self, with_map=True)
        self.frame_city.hide()

        self.layout.addStretch()
        self.layout.addWidget(self.frame_city)
        self.layout.addWidget(self.not_connected_label)
        self.layout.addStretch()
        self.h_layout.addWidget(self.go_offline_radio)
        self.h_layout.addStretch()
        self.h_layout.addWidget(self.retry_connection_btn)

        self.veriy_connection = TaskThread(_function=self._run_con)
        self.veriy_connection.finished.connect(self.on_finished)

        self.retry_connection_btn.clicked.connect(self.check_connection)

        self.layout.addLayout(self.h_layout)
        self.setLayout(self.layout)

    def _run_con(self):
        """
        Update location using internet connection.

        :return:
        """
        _dict = {}
        if connected_to_internet():
            try:
                public_ip = get_public_ip()
                _dict = get_location_from_ip(public_ip, ResourcesLocation().database_dir + '/ip_location.mmdb')
                if not self.verify_dict(_dict):
                    return None
            except Exception as e:
                log.exception('Could not get location using public ip. {}'.format(e))

        return _dict

    @staticmethod
    def verify_dict(_dict):
        """
        Verify the informations on dictionary by chekcing each value.
        Each value of this dictionary is important to determine prayer times.

        :param _dict:
        :return:
        """
        assert isinstance(_dict, dict)

        for value in _dict.values():
            if (value is None) or (not value):
                return False
        return True

    def location_ok(self, _dict):
        """
        Called when location has been found.

        :param _dict: city information dictionary.
        :return:
        """
        Settings().save_city_config(_dict)
        self.frame_city.show()
        self.frame_city.update_labels(City(_dict))

        self.go_offline_radio.show()
        self.not_connected_label.hide()
        self.located = True

    def location_nok(self):
        """
        Called when NO location has been found.

        :return:
        """
        self.frame_city.hide()
        self.not_connected_label.show()
        self.go_offline_radio.hide()
        self.located = False

    def on_finished(self):
        """
        Verification and localization thread finished.

        :return:
        """
        d = self.veriy_connection.return_value
        if d:
            self.location_ok(d)
        else:
            self.location_nok()

        self.initialized = True
        self.parent().completeChanged.emit()
        self.retry_connection_btn.setEnabled(True)
        self.overlay.hide()

    def check_connection(self):
        """
        Check if a connection is available and pre-activate.

        :return:
        """
        self.retry_connection_btn.setEnabled(False)
        self.overlay.show()
        self.veriy_connection.start()


class LocationOnlinePage(QtWidgets.QWizardPage):

    def __init__(self, parent=None):
        super(LocationOnlinePage, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.setTitle("Online Location Platform\n")
        self.setSubTitle("IP Geolocation tool helps you find the "
                         "approximate geographic location of your IP address along with some other useful "
                         "information TimeZone, Country Code, State etc. to determine prayer times settings.\n\n"
                         "IP address location information is provided by MaxMind database.")
        self.setPixmap(QtWidgets.QWizard.BannerPixmap, QPixmap(":/icons/wizard_map.png"))

        self.layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()

        self.h_layout.addStretch()

        self.online_frame = OnlineFrameWizard(self)

        self.layout.addWidget(self.online_frame)
        self.layout.addLayout(self.h_layout)

        self.setLayout(self.layout)

    def initializePage(self):
        self.online_frame.check_connection()
        return super(LocationOnlinePage, self).initializePage()

    def isComplete(self):
        return self.online_frame.initialized

    def cleanupPage(self):
        """
        Runned when page is canceled.

        :return:
        """
        return super(LocationOnlinePage, self).cleanupPage()

    def nextId(self):
        if self.online_frame.located and (not self.online_frame.go_offline_radio.isChecked()):
            return self.wizard().prayer_page_id
        else:
            return self.wizard().location_offline_page_id
