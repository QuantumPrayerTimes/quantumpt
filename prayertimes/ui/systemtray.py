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
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registrymixin import UniqueRegistryMixin
from prayertimes.core.common.registryproperties import RegistryProperties

from prayertimes.utils.widgets.floatingtext import PMXMessageOverlay


class SysTrayMenu(UniqueRegistryMixin, QtWidgets.QMenu):
    """
    Menu that appears when right clicking on System Tray Icon.
    """

    def __init__(self, parent=None):
        super(SysTrayMenu, self).__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self.setFixedWidth(150)

        self.addSeparator()

        self.exit_action = QtWidgets.QAction(QIcon(":/icons/systray_close.png"),
                                             "Exit", self)
        self.exit_action.triggered.connect(self._close)
        self.addAction(self.exit_action)

    @staticmethod
    def _close():
        """
        Close the whole program.

        :return:
        """
        Registry().execute("close_application")


class SystemTrayIcon(UniqueRegistryMixin, RegistryProperties, QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.setIcon(QIcon(':/icons/systray_icon.png'))
        self.setVisible(True)

        self.right_menu = SysTrayMenu(parent)
        self.setContextMenu(self.right_menu)

        self.activated.connect(self.on_tray_icon_activated)
        self.setToolTip("QuantumPrayerTimes")

    def on_tray_icon_activated(self, event):
        if event == QtWidgets.QSystemTrayIcon.Trigger:
            if self.global_frame.isHidden():
                self.global_frame.show()
            if self.global_frame.windowState() & Qt.WindowMinimized:
                self.global_frame.setWindowState(Qt.WindowActive)
            if self.global_frame.isVisible():
                self.global_frame.window().activateWindow()


class FloatingNotificationArea(QtWidgets.QFrame, PMXMessageOverlay):
    def __init__(self, parent=None):
        super(FloatingNotificationArea, self).__init__(parent)
        super(PMXMessageOverlay, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.ToolTip)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

        self.setAttribute(Qt.WA_TranslucentBackground)

        Registry().register_function("show_floating_notification", self.show_message_sys)

    def show_message_sys(self, _str, _time):
        """
        Show the floating text.

        :param _str: text appearing in the floating notification.
        :param _time: time notification should stay ative.
        :return:
        """
        self.show()

        # Change the message timer
        self.change_timer(_time)

        # Get information on the message frame to adapt it
        self.update_message(_str)

        # Update size of the current frame to fit the message
        w = self.message_overlay.frameGeometry().width()
        h = self.message_overlay.frameGeometry().height()
        self.resize(w + 5, h + 5)

        # Show the message
        self.show_message(_str)

    def message_faded_out(self):
        """
        Override function when message fade out to hide the frame area.

        :return:
        """
        self.hide()
        return super(FloatingNotificationArea, self).message_faded_out()

    def move_to(self, location):
        """
        Move a widget to a special place in screen.

        :param location: location where widget will be placed. (can be TopLeft - TopRight - BottomLeft - BottomRight)
        :return:
        """
        screen = QtWidgets.QApplication.desktop().availableGeometry()
        size = self.geometry()
        if location == 'TopLeft':
            self.move(0, 0)
        if location == 'TopRight':
            self.move((screen.width() - size.width()), 0)
        if location == 'BottomLeft':
            self.move(0, (screen.height() - size.height()))
        if location == 'BottomRight':
            self.move((screen.width() - size.width()), (screen.height() - size.height()))

    def showEvent(self, event):
        self.update_message_position()
        self.move_to(location='BottomRight')
        return super(FloatingNotificationArea, self).showEvent(event)

    def resizeEvent(self, *args, **kwargs):
        self.update_message_position()
        self.move_to(location='BottomRight')
        return super(FloatingNotificationArea, self).resizeEvent(*args, **kwargs)


class SysTrayPanel(UniqueRegistryMixin, QtWidgets.QFrame):
    """
    Panel that appears when athan is playing to give ability to stop it from this panel.
    It should be closed at the end of the athan OR if stop button is clicked.
    """

    show_systray_signal = pyqtSignal(str)
    hide_systray_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(SysTrayPanel, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.stop_athan_bt = QtWidgets.QPushButton("Stop Athan", clicked=self.stop_athan)
        self.close_tb = QtWidgets.QToolButton(clicked=self.hide_systray_panel)
        self.close_tb.setIcon(QIcon(":/icons/systray_close.png"))
        self.label = QtWidgets.QLabel("There is not athan playing ...", self)

        self.setFixedSize(300, 120)

        self.setWindowFlags(self.windowFlags() | Qt.ToolTip)
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

        self.layout.addWidget(self.close_tb, alignment=Qt.AlignRight)
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.stop_athan_bt)

        self.show_systray_signal[str].connect(self.show_systray_panel)
        self.hide_systray_signal.connect(self.hide_systray_panel)

    def __application_init__(self):
        Registry().register_signal("show_systray_panel", self.show_systray_signal)
        Registry().register_signal("hide_systray_panel", self.hide_systray_signal)

    def __application_clean__(self):
        pass

    def stop_athan(self):
        """
        Control the athan from notification to permit to stop athan without opening the application.

        :return:
        """
        log.debug("athan is stopped from system tray panel")
        Registry().execute("stop_current_athan")
        # Force hiding the system tray panel even if it is done in stop athan function (activated if needed)
        # self.hide_systray_panel()

    def show_systray_panel(self, _str):
        """
        Display the system tray panel with a message.

        :param _str: message displayed with the panel.
        :return:
        """
        log.debug("system tray panel appears")
        self.label.setText("{0}".format(_str))
        self.show()

    def hide_systray_panel(self):
        """
        Hide system tray panel.

        :return:
        """
        log.debug("system tray panel hides")
        self.hide()

    def move_to(self, location):
        """
        Move a widget to a special place in screen.

        :param location: location where widget will be placed. (can be TopLeft - TopRight - BottomLeft - BottomRight)
        :return:
        """
        screen = QtWidgets.QApplication.desktop().availableGeometry()
        size = self.geometry()
        if location == 'TopLeft':
            self.move(0, 0)
        if location == 'TopRight':
            self.move((screen.width() - size.width()), 0)
        if location == 'BottomLeft':
            self.move(0, (screen.height() - size.height()))
        if location == 'BottomRight':
            self.move((screen.width() - size.width()), (screen.height() - size.height()))

    def showEvent(self, event):
        self.move_to(location='BottomRight')
        return super(SysTrayPanel, self).showEvent(event)

    def resizeEvent(self, *args, **kwargs):
        self.move_to(location='BottomRight')
        return super(SysTrayPanel, self).resizeEvent(*args, **kwargs)
