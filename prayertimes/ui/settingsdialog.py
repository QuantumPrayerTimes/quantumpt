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
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QIcon, QColor, QStandardItem, QStandardItemModel, QFont
from PyQt6.QtSql import QSqlDatabase, QSqlQuery

from prayertimes.core.common import translate
from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registryproperties import RegistryProperties
from prayertimes.core.common.registrymixin import RegistryMixin
from prayertimes.core.common.resourceslocation import ResourcesLocation
from prayertimes.core.common.settings import Settings

from prayertimes.ui.abstract import (
    Dialog,
    ListView,
    SideLabel,
    ListWidgetSelectorFrame,
    FrameCitySetting,
)

from prayertimes.utils.city_infos import City, get_utc_offset


class SettingsFrameSelector(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(SettingsFrameSelector, self).__init__(parent)

        self.setFixedWidth(135)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.setSpacing(0)

        # self.side_label = QtWidgets.QLabel('Settings - الاعدادات')
        # self.side_label.setObjectName("TopSideLabel")

        self.sl_1 = SideLabel(
            parent=self,
            label=translate("Application", "General"),
            icon=None,
            w_colorframe=3,
            h_colorframe=45,
            alignment="left",
            color=QColor(255, 165, 0),
        )
        self.sl_2 = SideLabel(
            parent=self,
            label=translate("Application", "Location"),
            icon=None,
            w_colorframe=3,
            h_colorframe=45,
            alignment="left",
            color=QColor(255, 165, 0),
        )

        self.listwidget_frame = ListWidgetSelectorFrame(self)

        _item = QtWidgets.QListWidgetItem(self.listwidget_frame)
        _item.setSizeHint(self.sl_1.sizeHint())
        self.listwidget_frame.setItemWidget(_item, self.sl_1)

        _item = QtWidgets.QListWidgetItem(self.listwidget_frame)
        _item.setSizeHint(self.sl_2.sizeHint())
        self.listwidget_frame.setItemWidget(_item, self.sl_2)

        # Resize ListWidget to fit content
        self.listwidget_frame.setFixedSize(
            self.width(),
            self.listwidget_frame.sizeHintForRow(0) * self.listwidget_frame.count()
            + 2 * self.listwidget_frame.frameWidth(),
        )

        # self.layout.addWidget(self.side_label)
        self.layout.addWidget(self.listwidget_frame)
        self.layout.addStretch()

        # Set margin between frame and borders
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        # Set margin between elements of layout
        self.layout.setSpacing(0)

        self.layout.addLayout(self.h_layout)

        # # # # This whole code activate Toolbuttons inside the settings dialog # # # #
        # self.settings_dialog_tb = QtWidgets.QToolButton()
        # self.settings_dialog_tb.setObjectName("settings_button")
        # self.settings_dialog_tb.setFixedHeight(self.width() / 3)
        # self.info_dialog_tb = QtWidgets.QToolButton()
        # self.info_dialog_tb.setObjectName("info_button")
        # self.info_dialog_tb.setFixedHeight(self.width() / 3)
        # self.about_dialog_tb = QtWidgets.QToolButton()
        # self.about_dialog_tb.setObjectName("about_button")
        # self.about_dialog_tb.setFixedHeight(self.width() / 3)
        #
        # self.h_layout.addWidget(self.settings_dialog_tb)
        # self.h_layout.addWidget(self.info_dialog_tb)
        # self.h_layout.addWidget(self.about_dialog_tb)
        #
        # self.settings_dialog_tb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.info_dialog_tb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.about_dialog_tb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self.listwidget_frame.currentRowChanged.connect(self._modify_style_item)

    def _modify_style_item(self, idx):
        """
        Handle changing style whether a new item is selected.

        :param idx: index of the new item.
        :return:
        """
        self.parent().set_stack(idx)

        for idx_item in range(self.listwidget_frame.count()):
            item = self.listwidget_frame.item(idx_item)
            if item.isSelected():
                side_label_instance = self.listwidget_frame.itemWidget(item)
                side_label_instance.selected.emit()
            else:
                side_label_instance = self.listwidget_frame.itemWidget(item)
                side_label_instance.unselected.emit()


class MainSettingsFrame(RegistryMixin, QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(MainSettingsFrame, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.city_object = None
        self.grid_layout = QtWidgets.QGridLayout()

        self.listview_countries = ListView(self)
        self.country_model = QStandardItemModel()

        self.listview_cities = ListView(self)
        self.list_cities = {}
        self.city_model = QStringListModel()

        self._selected_country = ""
        self._selected_city = ""

        self.frame_city = FrameCitySetting(self)

        self.setup_ui()

    def setup_ui(self):
        """
        Setup the UI layout.

        :return:
        """
        self.grid_layout.addWidget(self.listview_countries, 0, 0)
        self.grid_layout.addWidget(self.listview_cities, 0, 1)
        self.grid_layout.addWidget(self.frame_city, 1, 0, 1, 2)

        self.setLayout(self.grid_layout)

    def __application_init__(self):
        self._init_database()
        # Check if settings file exists
        if os.path.isfile(Settings().fileName()):
            # Do something
            pass
        else:
            # Should never fall here
            Settings().set_up_default_values()
        pass

    def __application_post_init__(self):
        pass

    def __application_clean__(self):
        self.db.close()

    def _generate_countries(self):
        """
        Generate the country list and handle the display of these countries.

        :return:
        """
        query = QSqlQuery(self.db)
        query.exec("SELECT DISTINCT country, cc FROM DATABASE ORDER BY country ASC")

        while query.next():
            record = query.record()
            item = QStandardItem()
            item.setIcon(QIcon(":/icons/countries/{}.png".format(record.value("cc"))))
            item.setText(record.value("country"))
            self.country_model.appendRow(item)

        self.listview_countries.setModel(self.country_model)
        self.listview_countries.selectionModel().currentChanged.connect(
            self.modified_country
        )

    def _init_database(self):
        """
        Initialize the database and generates the coutries.

        :return:
        """
        self.db = QSqlDatabase("QSQLITE")
        self.db.setDatabaseName(ResourcesLocation().database_dir + "/database.db")
        if self.db.open():
            self._generate_countries()
        else:
            log.error("Cannot open database")

    @staticmethod
    def check_country_city(country, city):
        """
        Function that checks if country and city provided are in the database. (Not implemented yet)

        :param country: country to be checked.
        :param city: city to be checked.
        :return:
        """
        pass

    def modified_country(self, current, _):
        """
        Handle behavior when a country is selected from list.

        :param current: Current country selected.
        :param _: Previous country selected. [Not used]
        :return:
        """
        # Property @selected_country.setter will generate the list of cities
        self.selected_country = str(current.data())

    def modified_city(self, current, _):
        """
        Handle behavior when a city is selected from list.

        :param current: Current city selected.
        :param _: Previous city selected. [Not used]
        :return:
        """
        # Property @selected_city.setter will update frame display
        self.selected_city = str(current.data())

    @property
    def selected_country(self):
        return self._selected_country

    @selected_country.setter
    def selected_country(self, country):
        """
        Handle the generation of the cities list and the display of these cities.

        :param country:
        :return:
        """
        if country == "":
            return

        self._selected_country = country
        self._generate_cities(self.selected_country)
        self.city_object = None
        self.frame_city.clear()

    def _generate_cities(self, country):
        """
        Generate the cities list and handle the display of these cities.

        :param country: Country that needs to generate its cities.
        :return:
        """
        # Clear list and model before adding new elements
        self.list_cities.clear()
        self.city_model = QStringListModel([])

        query = QSqlQuery(self.db)
        query.exec(
            "SELECT id, state, district, city FROM DATABASE WHERE country='{}'".format(
                country
            )
        )

        while query.next():
            record = query.record()
            _city = record.value("city")
            _state = record.value("state")
            _district = record.value("district")
            _id = record.value("id")

            if _state or _district:
                if not _district:
                    text = "{city} [{state}]".format(city=_city, state=_state)
                elif not _state:
                    text = "{city} [{state}]".format(city=_city, state=_district)
                else:
                    text = "{city} [{state}] [{district}]".format(
                        city=_city, state=_state, district=_district
                    )
            else:
                text = "{city}".format(city=_city)

            self.list_cities[text] = _id

        self.city_model.setStringList(self.list_cities.keys())
        self.city_model.sort(0, Qt.SortOrder.AscendingOrder)

        self.listview_cities.setModel(self.city_model)
        self.listview_cities.selectionModel().currentChanged.connect(self.modified_city)

    @property
    def selected_city(self):
        return self._selected_city

    @selected_city.setter
    def selected_city(self, city):
        """
        Handle the update of the new selected city and update frame settings diplay.

        :param city: set the selected city and display informations.
        :return:
        """
        if city == "":
            return

        self._selected_city = city
        self._update_city_frame(self.list_cities[city])

    def _update_city_frame(self, city_id):
        """
        Generate informations about city from database id and update city frame settings.

        :param city_id: Database ID of the city
        :return:
        """
        query = QSqlQuery(self.db)
        query.exec("SELECT * FROM DATABASE WHERE id='{}'".format(city_id))

        while query.next():
            record = query.record()

            # Get dictionnary information from database of the selected city
            # and update our dictionnary with the correct values
            self.city_object = City(
                dict(
                    continent=record.value("continent"),
                    country=record.value("country"),
                    cc=record.value("cc"),
                    state=record.value("state"),
                    city=record.value("city"),
                    lat=record.value("lat"),
                    lng=record.value("lng"),
                    tz=record.value("tz"),
                    utc=get_utc_offset(record.value("tz")),
                )
            )

        # Update the display on frame
        self.frame_city.update_labels(self.city_object)

    def save_settings(self):
        """
        Save settings of current city informations and load this configuration into main frame.

        :return:
        """
        if self.city_object:
            Settings().save_city_config(self.city_object.city_info)
            log.debug(
                "saved city configuration from settings with : {}".format(
                    self.city_object.city_info
                )
            )
            Registry().execute("load_city_configuration")
        else:
            return

    # def showEvent(self, event):
    #     self.frame_city.clear()
    #     if self.listview_cities:
    #         self.listview_cities.setModel(QStringListModel([]))
    #         self.listview_cities.clearSelection()
    #     if self.listview_countries:
    #         self.listview_countries.clearSelection()
    #     return super(MainSettingsFrame, self).showEvent(event)


class GeneralSettingsFrame(RegistryProperties, QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(GeneralSettingsFrame, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.close_prog_cb = QtWidgets.QCheckBox(
            translate("Application", "Minimize to system tray when program is closed"),
            self,
        )
        self.splashscreen_cb = QtWidgets.QCheckBox(
            translate("Application", "Show splashscreen"), self
        )
        self.arabic_names_cb = QtWidgets.QCheckBox(
            translate("Application", "Show arabic prayer names"), self
        )

        self.layout.addWidget(self._groupbox_close_setting())
        self.layout.addStretch()

    def _groupbox_close_setting(self):
        """
        Generate groupbox for general settings.

        :return:
        """
        group_close = QtWidgets.QGroupBox("", self)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.close_prog_cb)
        vbox.addWidget(self.splashscreen_cb)
        vbox.addWidget(self.arabic_names_cb)
        group_close.setLayout(vbox)

        return group_close

    def save_settings(self):
        """
        Save current configuration.

        :return:
        """
        if self.close_prog_cb.isChecked():
            Settings().setValue("general_settings/close", 0)
        else:
            Settings().setValue("general_settings/close", 1)

        if self.splashscreen_cb.isChecked():
            Settings().setValue("general_settings/splashscreen", 1)
        else:
            Settings().setValue("general_settings/splashscreen", 0)

        if self.arabic_names_cb.isChecked():
            Settings().setValue("general_settings/arabic_names", 1)
            self.prayer_frame.update_prayer_name()
        else:
            Settings().setValue("general_settings/arabic_names", 0)
            self.prayer_frame.update_prayer_name()

    def load_settings(self):
        """
        Load settings to read settings each time dialog is opened and set the correct state for settings.

        :return:
        """
        if Settings().contains("general_settings/splashscreen"):
            if Settings().value("general_settings/splashscreen") == 0:
                self.splashscreen_cb.setChecked(False)
            elif Settings().value("general_settings/splashscreen") == 1:
                self.splashscreen_cb.setChecked(True)
            else:
                log.debug(
                    "value for splashscreen in "
                    "settings.ini: {}".format(
                        Settings().value("general_settings/splashscreen")
                    )
                )
        else:
            self.splashscreen_cb.setChecked(True)
            Settings().setValue("general_settings/splashscreen", 1)

        if Settings().contains("general_settings/arabic_names"):
            if Settings().value("general_settings/arabic_names") == 0:
                self.arabic_names_cb.setChecked(False)
            elif Settings().value("general_settings/arabic_names") == 1:
                self.arabic_names_cb.setChecked(True)
            else:
                log.debug(
                    "value for arabic_names in "
                    "settings.ini: {}".format(
                        Settings().value("general_settings/arabic_names")
                    )
                )
        else:
            self.arabic_names_cb.setChecked(True)
            Settings().setValue("general_settings/arabic_names", 1)

        if Settings().contains("general_settings/close"):
            if Settings().value("general_settings/close") == 0:
                self.close_prog_cb.setChecked(True)
            elif Settings().value("general_settings/close") == 1:
                self.close_prog_cb.setChecked(False)
            else:
                log.debug(
                    "value for close in settings.ini: {}".format(
                        Settings().value("general_settings/close")
                    )
                )
        else:
            self.close_prog_cb.setChecked(True)
            Settings().setValue("general_settings/close", 0)


class SettingsDialog(Dialog):
    """
    Settings dialog.
    """

    APPLY = QtWidgets.QDialogButtonBox.StandardButton.Apply
    CANCEL = QtWidgets.QDialogButtonBox.StandardButton.Cancel
    OK = QtWidgets.QDialogButtonBox.StandardButton.Ok

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(
            width=780,
            height=480,
            obj_name=self.__class__.__name__,
            titlebar_name="Settings",
            titlebar_icon=None,
            parent=parent,
        )

        self.dialog_buttons = QtWidgets.QDialogButtonBox(
            self.CANCEL | self.OK | self.APPLY, Qt.Orientation.Horizontal, self
        )

        self.apply_button = self.dialog_buttons.button(self.APPLY)
        self.cancel_button = self.dialog_buttons.button(self.CANCEL)
        self.ok_button = self.dialog_buttons.button(self.OK)

        self.apply_button.setFixedWidth(100)
        self.cancel_button.setFixedWidth(100)
        self.ok_button.setFixedWidth(100)

        # Cancel button signal
        self.dialog_buttons.rejected.connect(self.reject)
        # OK button signal
        self.dialog_buttons.accepted.connect(self.handle_ok)
        # Apply button signal
        self.apply_button.clicked.connect(self.handle_apply)

        self.status_layout = QtWidgets.QHBoxLayout()
        self.status_layout.setContentsMargins(9, 9, 9, 9)

        contact_label = QtWidgets.QLabel(
            translate("Application", "For any problem, please contact us."), self
        )
        font = QFont("ubuntu", 10)
        contact_label.setFont(font)

        self.status_layout.addWidget(contact_label)
        self.status_layout.addWidget(self.dialog_buttons)

        self.h_layout = QtWidgets.QHBoxLayout()

        self.right_side_panel = SettingsFrameSelector(self)
        self.stack = QtWidgets.QStackedWidget(self)

        self.general_settings_frame = GeneralSettingsFrame(self)
        self.main_settings_frame = MainSettingsFrame(self)

        self.stack.addWidget(self.general_settings_frame)
        self.stack.addWidget(self.main_settings_frame)

        self.layout.addLayout(self.h_layout)
        self.h_layout.addWidget(self.right_side_panel)
        self.h_layout.addWidget(self.stack)
        self.layout.addLayout(self.status_layout)

    def __application_init__(self):
        self.set_stack(0)

    def __application_post_init__(self):
        pass

    def __application_clean__(self):
        pass

    def showEvent(self, event):
        """
        Overring showEvent to update settings values from each frame each time the dialog is opened.

        :param event:
        :return:
        """
        self.general_settings_frame.load_settings()
        return super(SettingsDialog, self).showEvent(event)

    def set_stack(self, idx):
        """
        Set the visible widget to widget at index <idx>

        :param idx: index of the widget to be visible.
        :return:
        """
        self.stack.setCurrentIndex(idx)
        self.right_side_panel.listwidget_frame.setCurrentRow(idx)

    def handle_ok(self):
        """
        Ok button behaves exactly like apply buttons except it closes the dialog.

        :return:
        """
        self.handle_apply()
        self.accept()

    def handle_apply(self):
        """
        Save all configuration present in frames contained in settings dialog.

        :return:
        """
        self.general_settings_frame.save_settings()
        self.main_settings_frame.save_settings()
