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

from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.settings import Settings

from prayertimes.ui.abstract import GlobalTitlebar, AbstractGlobalFrame
from prayertimes.ui.principalframe import PrincipalFrame
from prayertimes.ui.systemtray import (
    SystemTrayIcon,
    FloatingNotificationArea,
    SysTrayPanel,
)

from prayertimes.utils.widgets.principaloverlay import PrincipalOverlay


class GlobalFrame(AbstractGlobalFrame):
    """
    Global Frame that holds all frames.
    """

    def __init__(self, parent=None):
        super(GlobalFrame, self).__init__(
            width=970, height=600, obj_name=self.__class__.__name__, parent=parent
        )

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.titlebar = GlobalTitlebar(self, title="QuantumPrayerTimes", icon=None)
        self.frame = PrincipalFrame(self)

        # Set margin between frame and borders
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # Set margin between elements of layout
        self.main_layout.setSpacing(0)

        self.main_layout.addWidget(self.titlebar)
        self.main_layout.addWidget(self.frame)

        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()

        PrincipalOverlay(self)
        FloatingNotificationArea(self)
        SysTrayPanel()

        Registry().register_function("close_application", self.close_application)
        Registry().register_function("hide_app_in_systray", self.hide_in_systray)
        Registry().register_function("activate_global_blur", self.activate_blur)
        Registry().register_function("desactivate_global_blur", self.desactivate_blur)

    def __application_init__(self):
        pass

    def __application_clean__(self):
        self.cleanup()

    @staticmethod
    def close_application():
        """
        This function handle the cleaning of all widgets and close the application.
        It is called when application is closed by user or a critical exception happens.

        :return:
        """
        Registry().execute("__application_clean__")
        QtWidgets.QApplication.instance().quit()

    def hide_in_systray(self):
        """
        Hide the application in the system tray.

        :return:
        """
        # self.fade_out()
        self.hide()  # hide() function calls close() funtion
        log.debug("Running in background...")
        Registry().execute(
            "show_floating_notification",
            "QuantumPrayerTimes program is still running in background",
            3000,
        )

    def cleanup(self):
        """
        Clean up the shedulers and remove application to avoid crashed.

        :return:
        """
        self.tray_icon.hide()
        self.hide()

        # Needed for Windows to stop crashes on exit
        Registry().remove("application")

    def closeEvent(self, event):
        """
        Handles the closing from Windows taskbar.

        :param event:
        :return:
        """
        if Settings().value("general_settings/close") == 1:
            self.close_application()
        elif Settings().value("general_settings/close") == 0:
            self.hide_in_systray()
        else:
            log.warning("Not defined, by default, use hide in system tray")
            Registry().execute("hide_app_in_systray")
        event.ignore()
