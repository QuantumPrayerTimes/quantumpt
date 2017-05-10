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

from prayertimes.core.common import translate
from prayertimes.core.common.registrymixin import UniqueRegistryMixin, Registry
from prayertimes.core.common.registryproperties import RegistryProperties
from prayertimes.core.common.settings import Settings

from prayertimes.core.lib.prayer.prayermanager import PrayerManager

from prayertimes.ui.controlframes import ControlOpacity, ControlVolume, ControlDua
from prayertimes.ui.prayerframe import PrayersContainerFrame

from prayertimes.utils.widgets.floatingtext import PMXMessageOverlay


class LineEdit(QtWidgets.QLineEdit, PMXMessageOverlay):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        super(PMXMessageOverlay, self).__init__()

        self.setObjectName(self.__class__.__name__)

        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self._city = ''
        self._country = ''
        self._icon = QtWidgets.QLabel('')

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._layout.addWidget(self._icon)
        self.setLayout(self._layout)

    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, value):
        self.setText(value)
        self._city = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, cc):
        self._icon.setPixmap(QPixmap(":/icons/countries/{}.png".format(cc)))


class ComboBox(QtWidgets.QComboBox):
    def __init__(self, list_items, parent=None):
        super(ComboBox, self).__init__(parent)

        assert isinstance(list_items, list)

        self.view = QtWidgets.QListView(self)
        self.setView(self.view)

        self.addItems(list_items)


class RoundedToolButton(QtWidgets.QToolButton):
    def __init__(self, obj_name, parent=None):
        super(RoundedToolButton, self).__init__(parent)

        self.setObjectName("{}TB".format(obj_name))
        self.setFixedSize(50, 50)


class MainFrame(UniqueRegistryMixin, RegistryProperties, QtWidgets.QFrame):
    """
    MainFrame that handle connection between graphical items and calculation methods from PrayerManager.
    """

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        PrayersContainerFrame(self)
        PrayerManager()

        self.setObjectName(self.__class__.__name__)

        self.layout = QtWidgets.QVBoxLayout()
        self.settings_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.asr_settings_list = ComboBox(list_items=[translate('Application', "Standard"),
                                                      translate('Application', "Hanafi")], parent=self)
        self.calc_method_list = ComboBox(list_items=self.prayer_manager.method_list, parent=self)

        # Set default calculation method to ISNA
        index = self.calc_method_list.findText("ISNA", Qt.MatchFixedString)
        self.calc_method_list.setCurrentIndex(index)

        self.top_label = QtWidgets.QLabel('Q', self)
        self.top_label.setObjectName("QTopLabel_welcome")
        self.top_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.top_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.line_edit = LineEdit(parent=self)
        self.line_edit.setFixedWidth(400)

        self.dua_after_athan_cb = QtWidgets.QCheckBox(translate('Application', "Run dua after athan"), self)
        self.dua_after_athan_cb.stateChanged.connect(self._set_dua_after_athan)

        self.volume_tb = RoundedToolButton(obj_name='Volume', parent=self)
        self.volume_tb.clicked.connect(self._control_volume)
        self.control_vol = ControlVolume(self)
        self.control_vol.hide()

        self.opacity_tb = RoundedToolButton(obj_name='Opacity', parent=self)
        self.opacity_tb.clicked.connect(self._control_opacity)
        self.control_op = ControlOpacity(self)
        self.control_op.hide()

        self.dua_tb = RoundedToolButton(obj_name='Dua', parent=self)
        self.dua_tb.clicked.connect(self._control_dua)
        self.control_dua = ControlDua(self)
        self.control_dua.hide()

        self.timeformat_tb = RoundedToolButton(obj_name='TimeFormat', parent=self)
        self.timeformat_tb.clicked.connect(self.udpate_date_format)
        self.timeformat_tb.setFixedSize(50, 50)

        self.style_tb = RoundedToolButton(obj_name='Style', parent=self)
        self.style_tb.clicked.connect(self.change_style)
        self.style_tb.setEnabled(False)

        self.athan_list = ComboBox(list_items=["Athan 1", "Athan 2", "Athan 3", "Athan 4",
                                               "Athan 5", "Athan 6", "Athan 7"], parent=self)
        self.athan_list.setFixedWidth(120)

        # TODO - Change button text when appropriate.
        self.preview_athan_button = QtWidgets.QPushButton("Preview")
        self.preview_athan_button.clicked[bool].connect(self._preview_athan)
        self.preview_athan_button.setFixedWidth(80)

        self.athan_list.currentIndexChanged[int].connect(self.change_athan)

        self.calc_method_list.currentIndexChanged.connect(self.update_calculation_method)
        self.asr_settings_list.currentIndexChanged.connect(self.update_asr_settings_method)

        self.setup_ui()

    def setup_ui(self):
        """
        Setup the UI layout.

        :return:
        """
        self.buttons_layout.addWidget(self.line_edit)
        self.buttons_layout.addWidget(self.calc_method_list)
        self.buttons_layout.addWidget(self.asr_settings_list)

        self.settings_layout.addWidget(self.style_tb)
        self.settings_layout.addStretch()
        self.settings_layout.addWidget(self.volume_tb)
        self.settings_layout.addWidget(self.opacity_tb)
        self.settings_layout.addWidget(self.dua_tb)
        self.settings_layout.addWidget(self.timeformat_tb)
        self.settings_layout.addStretch()
        self.settings_layout.addWidget(self.preview_athan_button)
        self.settings_layout.addWidget(self.athan_list)

        self.layout.addWidget(self.top_label)
        self.layout.addStretch()
        self.layout.addWidget(self.prayer_frame)
        self.layout.addLayout(self.buttons_layout)
        self.layout.addStretch()
        self.layout.addWidget(self.dua_after_athan_cb)
        self.layout.addStretch()
        self.layout.addLayout(self.settings_layout)

        self.setLayout(self.layout)

    def __application_init__(self):
        Registry().register_function("update_display_information", self.update_display_information)
        Registry().register_function("update_city_information", self.update_city_information)

    def __application_post_init__(self):
        pass

    def __application_clean__(self):
        pass

    def stop_current_athan(self):
        """
        Stop the current athan playing.

        :return:
        """
        self.media_manager.stop_current_athan()
        # Registry().execute("stop_current_athan")

    def reset_offset(self):
        """
        Reset all offsets to 0.

        :return:
        """
        self.prayer_manager.reset_offsets()
        # Registry().execute("reset_offsets")

    def udpate_date_format(self):
        """
        Update the time format display.

        :return:
        """
        self.prayer_manager.udpate_time_format()
        # Registry().execute("udpate_time_format")

    def _set_dua_after_athan(self):
        """
        Save the setting for dua after athan, the process is done when athan finishes.

        :return:
        """
        if self.dua_after_athan_cb.isChecked():
            Settings().setValue("prayer_settings/dua_after_athan", 1)
        else:
            Settings().setValue("prayer_settings/dua_after_athan", 0)

    def update_display_information(self, calc, asr_method, dua_after_athan, city_object):
        """
        Update the display information concerning the city, the calculation method, the
        asr setting method and dua after athan action.

        :param calc: calculation method.
        :param asr_method: asr setting method.
        :param dua_after_athan: dua after athan state.
        :param city_object:
        :return:
        """
        index = self.calc_method_list.findText(calc, Qt.MatchFixedString)
        self.calc_method_list.setCurrentIndex(index)

        index = self.asr_settings_list.findText(asr_method, Qt.MatchFixedString)
        self.asr_settings_list.setCurrentIndex(index)

        self.dua_after_athan_cb.setChecked(bool(dua_after_athan))

        self.update_city_information(city_object)

    def update_city_information(self, city_object):
        """
        Update the display information concerning the city.

        :param city_object:
        :return:
        """
        self.line_edit.city = city_object.city
        self.line_edit.icon = city_object.cc

    def _control_volume(self):
        """
        Control the volume frame display.

        Make sure to hide dua frame before.
        :return:
        """
        if self.control_vol.isHidden():
            # Make sure to close dua control if it's visible
            if self.control_dua.isVisible():
                self.control_dua.hide()
            self.control_vol.show()
            self.control_vol.setFocus(True)
        else:
            self.control_vol.hide()

    def _control_opacity(self):
        """
        Control the opacity frame display.

        Make sure to hide dua frame before.
        :return:
        """
        if self.control_op.isHidden():
            # Make sure to close dua control if it's visible
            if self.control_dua.isVisible():
                self.control_dua.hide()
            self.control_op.show()
            self.control_op.setFocus(True)
        else:
            self.control_op.hide()

    def _control_dua(self):
        """
        Control the dua frame display.

        :return:
        """
        if self.control_dua.isHidden():
            self.control_dua.show()
            self.control_dua.setFocus(True)
        else:
            self.control_dua.hide()

    @staticmethod
    def change_style():
        """
        Change application stylesheet.

        :return:
        """
        Registry().emit_signal("change_style")

    def _preview_athan(self):
        """
        Preview the current athan selected.

        :return:
        """
        idx = self.athan_list.currentIndex()
        self.media_manager.control_preview_athan(idx)
        # Registry().execute("control_preview_athan", idx)

    def update_calculation_method(self):
        """
        Update the calculation method.
        Called whether user change to a new calculation method.
        Saves value to settings and update prayer informations.

        :return:
        """
        Settings().setValue("prayer_settings/calculation", self.calc_method_list.currentText())
        Registry().execute("update_calculation_method", self.calc_method_list.currentText())

    def update_asr_settings_method(self):
        """
        Update the settings adjustment method.
        Called whether user change to a asr setting method.
        Saves value to settings and update prayer informations.

        :return:
        """
        Settings().setValue("prayer_settings/asr_method", self.asr_settings_list.currentText())
        Registry().execute("update_asr_settings", self.asr_settings_list.currentText())

    def change_athan(self, idx):
        """
        Change athans sound.

        :return:
        """
        self.media_manager.change_athan(idx)
