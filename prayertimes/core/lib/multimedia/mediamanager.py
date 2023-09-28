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

from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registryproperties import RegistryProperties
from prayertimes.core.common.registrymixin import UniqueRegistryMixin

from prayertimes.core.lib.multimedia.mediacore import (
    AthanPreviewPlayer,
    AthanMediaPlayer,
    RandomMediaPlayer,
)


class MediaManager(UniqueRegistryMixin, RegistryProperties):
    """
    Class to handle all media in program, it includes :
        Athan player (which include dua after athan)
        Athan preview player
        Dua timer player
    """

    # Shourouq is not included because it is not an athan
    __prayers_list__ = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

    def __init__(self):
        super(MediaManager, self).__init__(None)

        self.athan_preview = AthanPreviewPlayer()
        self.athan_player = AthanMediaPlayer()
        self.dua_player = RandomMediaPlayer()

        self.list_athan = self.athan_player.list_athans[:]

    def __application_init__(self):
        Registry().register_function("stop_current_athan", self.stop_current_athan)
        Registry().register_function("pause_all_athans", self.pause_all_athans)
        Registry().register_function("resume_all_athans", self.resume_all_athans)
        Registry().register_function("stop_preview_athan", self.stop_preview_athan)
        Registry().register_function(
            "control_preview_athan", self.control_preview_athan
        )
        Registry().register_function("change_current_athan", self.change_athan)

    def __application_clean__(self):
        self.stop_current_athan()
        self.stop_preview_athan()

    def stop_preview_athan(self):
        """
        Stop the current preview athan.

        :return:
        """
        if self.athan_preview.is_playing():
            self.athan_preview.stop()

    def control_preview_athan(self, idx):
        """
        Control the preview of the athan using the index provided.

        :param idx: index of athan chosen to be player.
        :return:
        """
        preview = self.list_athan[idx]
        if self.athan_preview.is_playing():
            self.athan_preview.stop()
        else:
            self.athan_preview.setup_media(preview)
            self.athan_preview.play()

    def stop_current_athan(self):
        """
        Check if athan is playing and stop running it.

        :return:
        """
        self.athan_player.stop()

    def pause_athan(self, prayer):
        """
        Pause the current athan corresponding to prayer name.

        :param prayer: prayer name.
        :return:
        """
        self.scheduler_manager.pause_job(job_id=prayer)

    def resume_athan(self, prayer):
        """
        Pause the current athan corresponding to prayer name.

        :param prayer: prayer name.
        :return:
        """
        self.scheduler_manager.resume_job(job_id=prayer)

    def pause_all_athans(self):
        """
        Pause all athans.
        To control state of athans, just need to check or uncheck activated_cb
        of the prayer time.

        :return:
        """
        self.prayer_frame.toggle_state_athan(activate=False)

    def resume_all_athans(self):
        """
        Resume all athans.
        To control state of athans, just need to check or uncheck activated_cb
        of the prayer time.

        :return:
        """
        self.prayer_frame.toggle_state_athan(activate=True)

    def run_athan(self, prayer_dict):
        """
        Run athan scheduler according to prayer times.

        :param prayer_dict: a dictionary with {prayer_name : time (datetime object)}.
        :return:
        """
        self.scheduler_manager.run_athan_scheduler(self.athan_player.play, prayer_dict)

    def change_athan(self, idx):
        """
        Change athan for athans scheduler.

        :param idx: index of athan chosen to be player.
        :return:
        """
        path = self.list_athan[idx]
        # Do not call setup_metia (will stop athan if already playing)
        self.athan_player.current_media = path

    def set_volume(self, vol):
        """
        Set volume to athans player.

        :param vol: new volume to set.
        :return:
        """
        self.athan_player.setup_volume(vol)
        # dua_after_athan player is inside athan_player object
        self.athan_player.dua_after_athan_player.setup_volume(vol)

        self.dua_player.setup_volume(vol)
        self.athan_preview.setup_volume(vol)

    def mute(self):
        """
        Set mute to current prayer athan playing.

        :return:
        """
        self.athan_player.setMuted(True)

    def unmute(self):
        """
        Disable mute for current prayer athan playing.

        :return:
        """
        self.athan_player.setMuted(False)
