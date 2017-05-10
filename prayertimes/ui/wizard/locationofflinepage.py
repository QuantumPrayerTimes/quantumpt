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
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

from prayertimes.core.common.logapi import log
from prayertimes.core.common.resourceslocation import ResourcesLocation
from prayertimes.core.common.settings import Settings

from prayertimes.ui.abstract import TaskThread, FrameCitySetting

from prayertimes.utils.city_infos import City
from prayertimes.utils.widgets.waitoverlay import WaitingOverlay


class CityCompleter(QtWidgets.QCompleter):

    def __init__(self, parent=None):
        super(CityCompleter, self).__init__(parent)
        self.popup().setObjectName(self.__class__.__name__)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setWrapAround(False)
        self.setFilterMode(Qt.MatchStartsWith)
        self.setMaxVisibleItems(7)  # Default value is 7

    def setModel(self, model):
        """
        Override setModel to set stylesheet after setting the model
        Needed to have stylesheet of completer's popup, must be set AFTER 'setModel'.

        :param model: model that completes suggestions.
        :return:
        """
        super(CityCompleter, self).setModel(model)
        self.popup().setItemDelegate(QtWidgets.QStyledItemDelegate(self))


class LineEditCityCompleter(QtWidgets.QLineEdit):

    def __init__(self, parent=None):
        super(LineEditCityCompleter, self).__init__(parent)
        self.setObjectName("LineEdit")
        self.setPlaceholderText("Please select your city")
        self.city_completer = CityCompleter(self)
        self.setCompleter(self.city_completer)


class OfflineFrameWizard(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(OfflineFrameWizard, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.initialized = False

        self.layout = QtWidgets.QVBoxLayout()

        self.overlay = WaitingOverlay(self)
        self.overlay.hide()

        self.line_edit = LineEditCityCompleter()
        self.frame_city = FrameCitySetting(self, with_map=True)
        self.frame_city.hide()

        self.layout.addWidget(self.line_edit)
        self.layout.addStretch()
        self.layout.addWidget(self.frame_city)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.line_edit.textChanged[str].connect(self.on_city_changed)
        self.line_edit.city_completer.activated[str].connect(self.on_selected_city)

        self.load_cities = TaskThread(_function=self.__set_database)
        self.load_cities.finished.connect(self.finished_loading)
        self.load_cities.start()

    def cleanup(self):
        """
        Cleanup the offline page.

        :return:
        """
        QSqlDatabase.removeDatabase(self.db.databaseName())

    def __set_database(self):
        self.db = QSqlDatabase('QSQLITE')
        self.db.setDatabaseName(ResourcesLocation().database_dir + '/database.db')
        if self.db.open():
            log.debug("Opened database")

    def set_completer(self, city):
        """
        Set the completer by creating a model of cities that have more than 3 letters.
        Avoir lag and memory resources problems.

        :param city: 4 first letters of the city.
        """

        query = QSqlQuery(self.db)
        query.exec("SELECT * from DATABASE WHERE (city LIKE '{}%')".format(city))

        model = QStandardItemModel()

        while query.next():
            record = query.record()
            item = QStandardItem()
            item.setIcon(QIcon(":/icons/countries/{}.png".format(str(record.value('cc')))))
            nam = "{}, {}, {}".format(record.value('city'), record.value('state'), record.value('country'))
            item.setText(nam)
            model.appendRow(item)

        self.line_edit.city_completer.setModel(model)

    @staticmethod
    def finished_loading():
        """
        Perform some tasks when cities loaded.
        """
        log.debug("OK finished loading cities")

    def _get_city_dict(self, db_id):
        """
        Use ID to get city dict (instead of city, state and country).

        :param db_id: database city ID.
        :return:
        """
        query = QSqlQuery(self.db)
        query.exec("SELECT * FROM DATABASE WHERE id={}".format(db_id))

        city_dict = {}

        while query.next():
            record = query.record()
            city_dict = dict(continent=record.value('continent'), city=record.value('city'),
                             state=record.value('state'), country=record.value('country'),
                             cc=record.value('cc'), lat=record.value('lat'),
                             lng=record.value('lng'), tz=record.value('tz'))
        return city_dict

    def on_city_changed(self, text):
        """
        Activate the completer only on 3 letters and more.

        :param text: text written in QLineEdit.
        :return:
        """
        if len(text) < 4:
            self.initialized = False
            self.parent().completeChanged.emit()
            self.line_edit.city_completer.setModel(None)
            return
        if not self.line_edit.city_completer.model():
            self.set_completer(text)

    def on_selected_city(self, text):
        """
        Use text to get city, state and country and then use these information
        to obtain city_dict.

        :param text: selected text in QCompleter, is composed of the city, state and country.
        :return:
        """
        [city, state, country] = list(map(str.strip, text.split(',')))
        query = QSqlQuery(self.db)
        query.exec("SELECT * FROM DATABASE WHERE city='{}' AND state='{}' "
                   "AND country='{}'".format(city, state, country))

        while query.next():
            record = query.record()
            city_dict = dict(continent=record.value('continent'), city=record.value('city'),
                             state=record.value('state'), country=record.value('country'),
                             cc=record.value('cc'), lat=record.value('lat'),
                             lng=record.value('lng'), tz=record.value('tz'))
            c = City(city_dict)
            self.frame_city.update_labels(c)
            self.frame_city.show()
            Settings().save_city_config(city_dict)

        self.initialized = True
        self.parent().completeChanged.emit()


class LocationOfflinePage(QtWidgets.QWizardPage):

    def __init__(self, parent=None):
        super(LocationOfflinePage, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.setTitle("Offline Location Platform\n")
        self.setSubTitle("Database Geolocation tool helps you find the "
                         "approximate geographic location of your city along with some other useful "
                         "information TimeZone, Country Code, State etc. to determine prayer times settings.\n\n"
                         "Database information is not very accurate and may contain errors, please verify before "
                         "proceed")
        self.setPixmap(QtWidgets.QWizard.BannerPixmap, QPixmap(":/icons/wizard_map.png"))

        self.layout = QtWidgets.QVBoxLayout(self)

        self.offline_frame = OfflineFrameWizard(self)
        self.offline_frame.show()

        self.layout.addWidget(self.offline_frame)

        self.setLayout(self.layout)

    def initializePage(self):
        # self.offline_frame.load_database()
        return super(LocationOfflinePage, self).initializePage()

    def isComplete(self):
        return self.offline_frame.initialized

    def cleanupPage(self):
        """
        Runned when page is canceled.

        :return:
        """
        # self.offline_frame.cleanup()
        return super(LocationOfflinePage, self).cleanupPage()

