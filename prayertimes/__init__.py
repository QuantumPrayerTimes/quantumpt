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

import io
import os
import sys
import time
import traceback

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSharedMemory, pyqtSignal, QCoreApplication, QFile, QTextStream
from PyQt5.QtGui import QIcon, QFontDatabase

from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.resourceslocation import ResourcesLocation
from prayertimes.core.common.settings import Settings

from prayertimes.core.lib.translator.translatormanager import LanguageManager

from prayertimes.ui.abstract import WelcomeNotification
from prayertimes.ui.exceptiondialog import CriticalExceptionDialog
from prayertimes.ui.globalframe import GlobalFrame
from prayertimes.ui.splashscreen import SplashScreen
from prayertimes.ui.wizard.firsttimewizard import QuantumPTWizard

# Initialise the resources
from prayertimes import resources


class QuantumPT(QtWidgets.QApplication):
    """
    The core application class. This class inherits from Qt's QApplication
    class in order to provide the core of the application.
    """

    welcome_message = 'This program is aimed to provide a local (without internet connection) way to calculate ' \
                      'prayer times and reminders. \n\nIt has been developed from scratch and may contains ' \
                      'bugs. \nDon\'t hesitate to send any report if you find a bug while using the program.'

    welcome_title = 'Welcome to Quantum Prayer Times (QuantumPT)'

    modify_style = pyqtSignal()

    def __init__(self, parent=None):
        super(QuantumPT, self).__init__(parent)

        Registry.create()

        # self.style = 0
        self.modify_style.connect(self.change_style)

        # Initialize language manager
        LanguageManager(language='en_US')

        # Add predefined fonts
        QFontDatabase.addApplicationFont(":/fonts/besmellah.ttf")
        QFontDatabase.addApplicationFont(":/fonts/capsuula.ttf")
        QFontDatabase.addApplicationFont(":/fonts/ubuntu.ttf")

        # Set stylesheet as Qt resource
        stylesheet = QFile(":/styles/default.css")
        stylesheet.open(QFile.ReadOnly | QFile.Text)

        self.stylesheet = QTextStream(stylesheet).readAll()
        self.setStyleSheet(self.stylesheet)

        # Use ico file so it can handle multiple sizes
        self.setWindowIcon(QIcon(":/icons/app.ico"))

        self.setApplicationDisplayName("QuantumPrayerTimes")
        self.setApplicationName("QuantumPrayerTimes")

        self.setOrganizationName('QuantumPrayerTimes')
        self.setOrganizationDomain('quantumprayertimes.github.io')

        self.setEffectEnabled(Qt.UI_AnimateCombo, False)
        self.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        Registry().register_signal("change_style", self.modify_style)

    def change_style(self):
        """
        Change stylesheet.

        :return:
        """
        pass
        # if self.style == 0:
        #     self.setStyleSheet(open("resources/styles/white.css").read())
        #     self.style = 1
        # else:
        #     self.setStyleSheet(open("resources/styles/default.css").read())
        #     self.style = 0

    def exec_(self):
        """
        Override exec method to allow the shared memory to be released on exit
        """
        result = QtWidgets.QApplication.exec_()
        # This function seems to cause problem in Ubuntu Linux because shared memory is not released.
        self.shared_memory.detach()
        return result

    def run(self):
        """
        Run the QuantumPT application.x
        """
        activate_first_notification = False

        # First time checks in settings
        has_run_wizard = Settings().value('general_settings/wizard_runned')
        if not has_run_wizard:
            first_wizard = QuantumPTWizard(parent=None)
            if first_wizard.exec_() == QtWidgets.QDialog.Accepted:
                Settings().setValue('general_settings/wizard_runned', 1)
                # Create the first notification only after wizard has been completed
                activate_first_notification = True
            elif first_wizard.was_cancelled:
                QCoreApplication.exit()
                sys.exit()

        # Show the SplashScreen
        show_splash = Settings().value('general_settings/splashscreen')
        if show_splash:
            splash = SplashScreen()
            splash.start_splashscreen.emit()

        # Start the main app window
        self.global_frame = GlobalFrame()

        # Make sure Qt really display the splash screen
        self.processEvents()
        self.global_frame.repaint()
        self.processEvents()

        Registry().execute('__application_init__')
        Registry().execute('__application_post_init__')

        self.processEvents()

        self.global_frame.show()

        # Show first notification program
        if activate_first_notification:
            WelcomeNotification(self.global_frame).notify(WelcomeNotification.OK, self.welcome_message,
                                                          self.welcome_title, button_text='Bismillah / بسم الله')

        if show_splash:
            # now kill the splashscreen
            splash.finish(self.global_frame)
            log.debug('Splashscreen closed')

        # For debug
        # WelcomeNotification(self.global_frame).notify(WelcomeNotification.ERROR, self.welcome_message,
        #                                               self.welcome_title, button_text='Bismillah / بسم الله')

        # Need to implement update checker
        # update_check = Settings().value('general_settings/update_check')
        # if update_check:
        #     process

        return self.exec_()

    def is_already_running(self):
        """
        Look to see if QuantumPT is already running and ask if a 2nd instance is to be started.
        """
        self.shared_memory = QSharedMemory('QuantumPT')
        if self.shared_memory.attach():
            log.error("It's already running")
            return True
        else:
            self.shared_memory.create(1)
            return False

    def set_busy_cursor(self):
        """
        Sets the Busy Cursor for the Application
        """
        self.setOverrideCursor(Qt.BusyCursor)
        self.processEvents()

    def set_normal_cursor(self):
        """
        Sets the Normal Cursor for the Application
        """
        self.restoreOverrideCursor()
        self.processEvents()


def hook_exception(exc_type, exc_value, tracebackobj):
    """
    Global function to catch unhandled exceptions.
    Add an exception hook so that any uncaught exceptions are displayed in this window rather than somewhere where
    users cannot see it and cannot report when we encounter these problems.

    :param exc_type: The class of exception.
    :param exc_value: The actual exception object.
    :param tracebackobj: A traceback object with the details of where the exception occurred.
    """
    instance = QuantumPT.instance()

    # KeyboardInterrupt is a special case.
    # We don't raise the error dialog when it occurs.
    if issubclass(exc_type, KeyboardInterrupt):
        if instance:
            instance.closeAllWindows()
        return

    separator = '-' * 80

    log_crash_file = ResourcesLocation().logs_dir + "/crash.log"
    log_dir = os.path.dirname(os.path.realpath(log_crash_file))

    # Create log dir to report crash and logging
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    notice = \
        """An unhandled exception occurred. Please report the problem\n""" \
        """using the error reporting dialog or via email to {}.\n""" \
        """A log has been written to "{}".\n\nError information:\n""".format("quantumprayertimes@gmail.com",
                                                                             log_crash_file)
    time_string = time.strftime("%Y-%m-%d, %H:%M:%S")

    tbinfofile = io.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(exc_type), str(exc_value))

    sections = [separator, time_string, separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)

    with open(log_crash_file, 'w') as f:
        try:
            f.write(msg)
        except OSError:
            pass

    error_box = CriticalExceptionDialog()
    error_box.text_edit.setText(str(notice) + str(msg))
    if not error_box.exec_():
        Registry().execute("close_application")
        QtWidgets.QApplication.instance().quit()


def main():
    """
    The main function which parses command line options and then runs
    """
    # Add path to qt_plugins instead of having mediaservice, platforms and sqldrivers in main
    # directory, currently : plugins/mediaservice - plugins/platforms - plugins/sqldrivers
    QtWidgets.QApplication.addLibraryPath(os.path.join(ResourcesLocation().root_dir, 'plugins'))

    # Now create and actually run the application.
    quantum_app = QuantumPT(sys.argv)

    log.info('Running program')
    log.info('INI file: %s', Settings.file_path)

    Registry().register('application', quantum_app)
    quantum_app.setApplicationVersion("v0.0.1")
    # Registry().execute("restore_default_settings")

    # Instance check
    if quantum_app.is_already_running():
        sys.exit()

    sys.excepthook = hook_exception
    sys.exit(quantum_app.run())
