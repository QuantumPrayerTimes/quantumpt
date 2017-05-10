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

import datetime
from functools import partial

from prayertimes.core.common.logapi import log
from prayertimes.core.common.registrymixin import UniqueRegistryMixin, Registry
from prayertimes.core.common.registryproperties import RegistryProperties
from prayertimes.core.common.settings import Settings

from prayertimes.core.lib.multimedia.mediamanager import MediaManager
from prayertimes.core.lib.prayer.prayertimes import PrayTimes
from prayertimes.core.lib.prayer.utils import dt_from_string, from_12_to_24, from_24_to_12, get_hour_minute
from prayertimes.core.lib.scheduler.schedulermanager import SchedulerManager

from prayertimes.utils.city_infos import City
from prayertimes.utils.date_timezone import get_utc_offset


class PrayerManager(UniqueRegistryMixin, RegistryProperties):
    """
    Class to control prayertimes times.
    """

    prayer_list = PrayTimes.prayer_list
    method_list = PrayTimes.method_list

    def __init__(self):

        super(PrayerManager, self).__init__(None)

        # Handle the audio part
        MediaManager()

        # Handle the scheduler part
        SchedulerManager()

        self.city_object = City({})

        # Default configuration is ISNA and 24h format
        self.praytimes = PrayTimes('ISNA', format_time="24h")
        self.date = datetime.datetime.today()

        # Structures used for calculation of the prayertimes
        self.praytimes_datetime = {}
        self.praytimes_offset = {}
        self.praytimes_settings = {}

        for p_name in self.prayer_frame.praytimes.keys():
            self.prayer_frame.praytimes[p_name].adjust_pt.valueChanged.connect(partial(self.adjust_offset,
                                                                                       prayer=p_name))
            self.prayer_frame.praytimes[p_name].activated_cb.stateChanged.connect(partial(self.state_control_athan,
                                                                                          prayer=p_name))
            self.prayer_frame.praytimes[p_name].mute_cb.stateChanged.connect(partial(self.mute_control_athan,
                                                                                     prayer=p_name))

    def __application_init__(self):
        Registry().register_function("update_prayer_scheduler", self.update_prayer_scheduler)
        Registry().register_function("update_calculation_method", self.update_calculation)
        Registry().register_function("update_asr_settings", self.update_asr_settings)
        Registry().register_function("udpate_time_format", self.udpate_time_format)
        Registry().register_function("validate_prayertimes", self.valid_prayertime)
        Registry().register_function("load_city_configuration", self.load_city_settings)
        if not Settings().allKeys():
            Settings().set_up_default_values()
        self.load_prayer_settings()

    def __application_clean__(self):
        pass

    def _calculate_prayer(self):
        """
        Calculate prayertimes times and then update display.

        # praytimes_datetime (dictionary) :
        # <keys>        <values>
        # Fajr      |   04:09 (datetime object)
        # Shourouq  |   05:51 (datetime object)
        # Dhuhr     |   13:24 (datetime object)
        # Asr       |   17:26 (datetime object)
        # Maghrib   |   20:57 (datetime object)
        # Isha      |   22:39 (datetime object)

        :return:
        """
        if self.city_object.city == "" or (self.city_object.lat == 0 and self.city_object.lng == 0):
            log.error("city empty, or latitude and longitude empty")
            return

        # Update calculation method
        calc = Settings().value("prayer_settings/calculation")
        if not calc:
            calc = 'ISNA'
            log.error("Big error ! Should never fall here")
        self.praytimes.set_method(calc)

        # Adjust settings
        self.praytimes.adjust(self.praytimes_settings)

        # Tune offsets
        for p_name in self.prayer_list:
            # Get the current value of each spinbox
            value = self.prayer_frame.praytimes[p_name].offset
            self.praytimes_offset[p_name.lower()] = value

        self.praytimes.tune(self.praytimes_offset)

        # Update the date and according UTC offset.
        self.date = datetime.datetime.today()
        self.city_object.utc = get_utc_offset(timezone=self.city_object.tz, date=self.date)

        # Calculate prayertimes times
        times = self.praytimes.get_times(date=self.date, coords=(self.city_object.lat, self.city_object.lng),
                                         utc_offset=self.city_object.utc)

        for prayer in self.prayer_list:
            time_ = str(times[prayer.lower()]).strip()
            log.debug("{0:<10} | {1:^12}".format(prayer, time_))
            self.prayer_frame.praytimes[prayer].time = time_

            # Update praytimes_datetime dictionnary, always work with 24h format
            if self.praytimes.time_format == "12h":
                self.praytimes_datetime[prayer] = dt_from_string(from_12_to_24(time_))
            else:
                self.praytimes_datetime[prayer] = dt_from_string(time_)

        log.debug("=====================")
        log.debug("Method used : {}".format(self.praytimes.calc_method))
        log.debug("=====================")

        self._get_current_prayer()

    def _get_current_prayer(self):
        """
        Get the current prayertimes.

        :return:
        """

        if not self.valid_prayertime():
            # Set default highlights to all prayertimes if error on prayertimes times
            return

        current_time = datetime.datetime.now().time()

        if self.praytimes_datetime["Fajr"] < current_time < self.praytimes_datetime["Shourouq"]:
            self.prayer_frame.set_current_prayer("Fajr")

        elif self.praytimes_datetime["Shourouq"] < current_time < self.praytimes_datetime["Dhuhr"]:
            self.prayer_frame.set_current_prayer(None)

        elif self.praytimes_datetime["Dhuhr"] < current_time < self.praytimes_datetime["Asr"]:
            self.prayer_frame.set_current_prayer("Dhuhr")

        elif self.praytimes_datetime["Asr"] < current_time < self.praytimes_datetime["Maghrib"]:
            self.prayer_frame.set_current_prayer("Asr")

        elif self.praytimes_datetime["Maghrib"] < current_time < self.praytimes_datetime["Isha"]:
            self.prayer_frame.set_current_prayer("Maghrib")
        else:
            self.prayer_frame.set_current_prayer("Isha")

    def adjust_offset(self, prayer):
        """
        Adjust the offsets chosen by user for the prayer.
        Use an offset dictionnary to store values.

        :param prayer: prayer that needs its offset to be modifed.
        :return:
        """
        log.debug("Adjusting offset for prayertimes {}".format(prayer))

        if self.city_object.city == "" or (self.city_object.lat == 0 and self.city_object.lng == 0):
            log.error("city empty, or latitude and longitude empty")
            return

        dt_time = self.praytimes_datetime[prayer]
        value = self.prayer_frame.praytimes[prayer].offset

        self.praytimes_offset[prayer] = value
        Settings().setValue("prayer_offsets/{}".format(prayer), value)

        if not isinstance(self.praytimes_datetime[prayer], datetime.time):
            log.error("Error : {} is not a datetime object".format(prayer))
            return

        if value == 0:
            # Keep the original value if 0
            dt = get_hour_minute(dt_time)
            if self.praytimes.time_format == "24h":
                self.prayer_frame.praytimes[prayer].time = dt
            else:
                self.prayer_frame.praytimes[prayer].time = from_24_to_12(dt)

        # Combine the current date and time and add delta from spinbox value
        complete_date_combined = datetime.datetime.combine(self.date, dt_time) + datetime.timedelta(minutes=value)

        # Get only the time format and formatting with hh:mm
        time_formatted = get_hour_minute(complete_date_combined.time())

        if self.praytimes.time_format == "24h":
            self.prayer_frame.praytimes[prayer].time = time_formatted
        else:
            self.prayer_frame.praytimes[prayer].time = from_24_to_12(time_formatted)

        self._calculate_prayer()
        self.scheduler_manager.reschedule_athan(prayer, self.praytimes_datetime[prayer])

    def load_prayer_settings(self):
        """
        Load informations from settings.ini (configuration file).

        :return:
        """
        self.city_object.city_info = Settings().load_city_config()

        # Calculate prayertimes times
        self._calculate_prayer()

        # Run schedulers correspnding to athans
        self.media_manager.run_athan(self.praytimes_datetime)

        # Update offsets display
        for p_name in self.prayer_list:
            value_offset = Settings().value("prayer_offsets/{}".format(p_name.lower()))
            self.praytimes_offset[p_name.lower()] = value_offset
            self.prayer_frame.set_offset(p_name, int(value_offset))

        # Update settings display
        calc = Settings().value("prayer_settings/calculation")
        asr_method = Settings().value("prayer_settings/asr_method")
        dua_after_athan = Settings().value("prayer_settings/dua_after_athan")

        Registry().execute("update_display_information", calc, asr_method, dua_after_athan, self.city_object)

        # Run scheduler that calculates prayertimes times every day
        self.scheduler_manager.run_calc_sched(func=self.update_prayer_scheduler)

    def load_city_settings(self):
        """
        Load informations for a new city and reschedules athan according to
        new prayer times calculated for the new city.

        :return:
        """
        self.city_object.city_info = Settings().load_city_config()
        Registry().execute("update_city_information", self.city_object)

        self.update_prayer_scheduler()

    def udpate_time_format(self):
        """
        Update time format without calculating again Prayer Times.

        :return:
        """
        if self.praytimes.time_format == "24h":
            self.praytimes.time_format = "12h"
        else:
            self.praytimes.time_format = "24h"

        # Get the current time displayed, parse it to time format and update display
        for prayer in self.prayer_list:
            try:
                if self.praytimes.time_format == "24h":
                    current_time = self.prayer_frame.praytimes[prayer.title()].time
                    format_time = from_12_to_24(current_time)
                    self.prayer_frame.praytimes[prayer.title()].time = format_time

                if self.praytimes.time_format == "12h":
                    current_time = self.prayer_frame.praytimes[prayer.title()].time
                    format_time = from_24_to_12(current_time)
                    self.prayer_frame.praytimes[prayer.title()].time = format_time
            except ValueError:
                log.exception("Error changing time format for {}".format(prayer))
                continue

    def reset_offsets(self):
        """
        Reset all offsets to zero and update display.

        :return:
        """
        # Check if all values of offsets are 0
        if all(value == 0 for value in self.praytimes_offset.values()):
            return

        for p_name in self.prayer_list:
            if self.praytimes_offset[p_name.lower()] == 0:
                continue
            else:
                self.praytimes_offset[p_name.lower()] = 0
                # Reset display value to 0
                self.prayer_frame.reset_offsets()

        self.update_prayer_scheduler()

    def valid_prayertime(self):
        """
        Verify that all prayertimes times are correct datetime.time object.

        :return:
        """
        for prayer in self.prayer_list:
            if not isinstance(self.praytimes_datetime[prayer], datetime.time):
                log.error("Error : {} is not a datetime object".format(prayer))
                return False
        return True

    def update_calculation(self, calc):
        """
        Update calcumation method and calculate athan prayertimes times according to settings.
        Re-schedule all athans because this setting modifies all prayertimes times.

        :param calc: calcumation method that will be used.
        :return:
        """
        self.praytimes.set_method(calc)
        self.update_prayer_scheduler()

    def update_asr_settings(self, settings):
        """
        Update asr settings and calculate athan prayertimes times according to settings.
        Re-schedule 'Asr' athan only because this setting only modifies 'Asr' prayertimes time.

        :param settings: asr settings method.
        :return:
        """
        if settings != 'Hanafi' and settings != 'Standard':
            log.error("Please be sure to select a correct asr settings")
        self.praytimes_settings["asr"] = settings
        self.praytimes.adjust(self.praytimes_settings)

        # Re-schedule only asr
        self._calculate_prayer()
        self.scheduler_manager.reschedule_athan(prayer='Asr', time=self.praytimes_datetime['Asr'])

    def update_prayer_scheduler(self):
        """
        Function to be run each day at midnight:
            > Calculate new prayertimes times
            > Re-schedule athans every day according to this calculation
            > Update prayer name

        :return:
        """
        # Calculate prayertimes times every day
        self._calculate_prayer()

        # Re-schedule athans every day according to new calculated prayertimes times
        self.scheduler_manager.reschedule_all_athans(self.praytimes_datetime)

        # Update prayer name (English/Arabic or Friday)
        self.prayer_frame.update_prayer_name()

    def state_control_athan(self, prayer):
        """
        Control the prayertimes athan (pause or running).

        :return:
        """
        if self.prayer_frame.praytimes[prayer].activated_cb.isChecked():
            log.debug("Activate prayer: {}".format(prayer))
            self.media_manager.resume_athan(prayer)
        else:
            log.debug("Desactivate prayer: {}".format(prayer))
            self.media_manager.pause_athan(prayer)

    def mute_control_athan(self, prayer):
        """
        Control the prayertimes athan (mute or unmute).

        :return:
        """
        if self.prayer_frame.praytimes[prayer].mute_cb.isChecked():
            log.debug("Mute prayer: {}".format(prayer))
            self.media_manager.mute()
        else:
            log.debug("Unmute prayer: {}".format(prayer))
            self.media_manager.unmute()
