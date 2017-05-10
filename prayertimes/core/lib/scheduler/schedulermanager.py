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

from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registrymixin import UniqueRegistryMixin
from prayertimes.core.common.registryproperties import RegistryProperties

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


class SchedulerManager(UniqueRegistryMixin, RegistryProperties):
    """
    Class to handle all tasks that needs to be scheduled in one scheduler, it includes :
        Athan scheduler in <MemoryJobStore> 'athans'
        Dua timer player in <MemoryJobStore> 'dua'
        Calculation prayer in <MemoryJobStore> 'calculation'
    """

    # Shourouq is not included because it is not an athan
    __prayers_list__ = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

    def __init__(self):
        super(SchedulerManager, self).__init__(None)

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_jobstore(MemoryJobStore(), alias='athans')
        self.scheduler.add_jobstore(MemoryJobStore(), alias='dua')
        self.scheduler.add_jobstore(MemoryJobStore(), alias='calculation')

    def __application_init__(self):
        Registry().register_function("shutdown_scheduler", self.shutdown)

    def __application_clean__(self):
        self.shutdown(wait=False)

    def run_athan_scheduler(self, func, prayertimes_dict):
        """
        Run the background scheduler for athan at a certain hour.
        Use datetime parameter.

        :param func: trigger functions.
        :param prayertimes_dict: a dictionary with {prayer_name : time (datetime object)}.
        :return:
        """

        for prayer, time in prayertimes_dict.items():
            if prayer == 'Shourouq':
                continue
            if not self.scheduler.get_job(prayer):
                log.debug("Adding job ID : {} in scheduler at time {}".format(prayer, time))
                kwargs = dict(prayer=prayer)
                trigger = CronTrigger(hour=time.hour, minute=time.minute)
                self.scheduler.add_job(func, kwargs=kwargs, jobstore='athans', trigger=trigger, id=prayer)

        if not self.scheduler.running:
            self.scheduler.start()

    def reschedule_athan(self, prayer, time):
        """
        Reschedule prayer time athan according to new prayer times.

        :param prayer: prayer name.
        :param time: a datetime.time object corresponding to new scheduled time for prayer.
        :return:
        """
        if prayer == 'Shourouq':
            return
        try:
            h = int(time.hour)
            m = int(time.minute)
            trigger = CronTrigger(hour=h, minute=m)
            # Keep state of the scheduler after rescheduling a job
            if self.scheduler.get_job(prayer).next_run_time:
                self.scheduler.reschedule_job(job_id=prayer, trigger=trigger, jobstore='athans')
            else:
                self.scheduler.reschedule_job(job_id=prayer, trigger=trigger, jobstore='athans')
                self.scheduler.pause_job(prayer)
        except AttributeError:
            log.error("Could not rescheduler athan alarm for {}".format(prayer))

        if not self.scheduler.running:
            self.scheduler.start()

    def reschedule_all_athans(self, prayer_dict):
        """
        Reschedule all athans time according to new prayer times.

        :param prayer_dict: a dictionary with {prayer_name : time (datetime object)}.
        :return:
        """
        for p_name, p_time in prayer_dict.items():
            if p_name in self.__prayers_list__:
                self.reschedule_athan(p_name, p_time)

    def run_dua_scheduler(self, func, minutes):
        """
        Run the background scheduler for duas every <minutes> minutes.

        :param func: trigger functions.
        :param minutes: interval minutes between duas.
        :return:
        """

        if not self.scheduler.get_job("Dua"):
            trigger = IntervalTrigger(minutes=minutes)
            self.scheduler.add_job(func, trigger=trigger, id="Dua", jobstore='dua')

        if not self.scheduler.running:
            self.scheduler.start()

    def reschedule_dua(self, minutes):
        """
        Reschedule dua according to new minute interval.

        :param minutes: interval minutes between duas.
        :return:
        """
        try:
            trigger = IntervalTrigger(minutes=minutes)
            self.scheduler.reschedule_job(job_id="Dua", trigger=trigger, jobstore='dua')
        except AttributeError:
            log.error("Could not rescheduler dua")

        if not self.scheduler.running:
            self.scheduler.start()

    def stop_dua_scheduler(self):
        """
        Stop the current dua playing and shutdown scheduler.

        :return:
        """
        self.scheduler.remove_job(job_id="Dua", jobstore='dua')

    def run_calc_sched(self, func):
        """
        Run scheduler for calculate prayertimes times automatically every day.

        :param func: trigger functions.
        :return:
        """

        if not self.scheduler.get_job("Calculation"):
            log.debug("Adding job ID : {} in scheduler".format("Calculation"))
            trigger = CronTrigger(hour='00', minute='00', second='01')
            self.scheduler.add_job(func, trigger=trigger, id="Calculation", jobstore='calculation')

        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self, *args, **kwargs):
        """
        shutdown all scheduler and jobs associated.

        :return:
        """
        if self.scheduler.running:
            self.scheduler.shutdown(*args, **kwargs)

    def display_info(self):
        """
        Display info about scheduler and scheduled jobs in which jobstore.

        :return:
        """
        self.scheduler.print_jobs()

    def resume_job(self, job_id, jobstore=None):
        """
        Resume a job present in jobstore.

        :param job_id: id of the job to be resumed.
        :param jobstore: jobstore where job id is.
        :return:
        """
        self.scheduler.resume_job(job_id, jobstore=jobstore)

    def pause_job(self, job_id, jobstore=None):
        """
        Pause a job present in jobstore.

        :param job_id: id of the job to be paused.
        :param jobstore: jobstore where job id is.
        :return:
        """
        self.scheduler.pause_job(job_id, jobstore=jobstore)
