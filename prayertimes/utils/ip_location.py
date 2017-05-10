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

import re
import random
import requests

import geoip2.database

from prayertimes.core.common.logapi import log


class IPgetter(object):
    """
    This class is designed to fetch your external IP address from the internet.
    It is used mostly when behind a NAT.
    It picks your IP randomly from a serverlist to minimize request overhead
    on a single server
    """

    def __init__(self):
        self.server_list = \
            ['http://ip.dnsexit.com',
             'http://ipecho.net/plain',
             'http://www.my-ip-address.net/',
             'http://myexternalip.com/raw',
             'http://www.canyouseeme.org/',
             'http://www.trackip.net/',
             'http://icanhazip.com/',
             'http://www.ipchicken.com/',
             'http://whatsmyip.net/',
             'http://www.ip-adress.com/',
             'http://checkmyip.com/',
             'http://www.tracemyip.org/',
             'http://www.lawrencegoetz.com/programs/ipinfo/',
             'http://ipgoat.com/',
             'http://www.myipnumber.com/my-ip-address.asp',
             'http://formyip.com/',
             'http://www.displaymyip.com/',
             'http://www.bobborst.com/tools/whatsmyip/',
             'http://www.geoiptool.com/',
             'https://www.whatsmydns.net/whats-my-ip-address.html',
             'http://myexternalip.com/',
             'http://www.ip-adress.eu/',
             'http://www.infosniper.net/',
             'https://wtfismyip.com/text',
             'http://ipinfo.io/',
             'http://httpbin.org/ip',
             'http://ip.ajn.me',
             'https://diagnostic.opendns.com/myip',
             'https://api.ipify.org']

    def get_externalip(self):
        """
        This function gets your IP from a random server.

        :return:
        """
        my_ip = ''
        for i in range(7):
            my_ip = self.fetch(random.choice(self.server_list))
            if my_ip != '':
                return my_ip
            else:
                continue
        return my_ip

    @staticmethod
    def fetch(server):
        """
        This function gets your IP from a specific server.

        :param server:
        :return:
        """
        request = None
        session = requests.Session()

        try:
            request = session.get(server, timeout=2)
            content = request.text

            m = re.search(
                '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
                '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
                content)
            myip = m.group(0)
            return myip if len(myip) > 0 else ''
        except (requests.ConnectionError, requests.ConnectTimeout):
            log.error("Error on server {}".format(server))
            return ""
        finally:
            if request:
                request.close()

    def test(self):
        """
        This functions tests the consistency of the servers
        on the list when retrieving your IP.
        All results should be the same.

        :return:
        """
        resultdict = {}
        for server in self.server_list:
            resultdict.update(**{server: self.fetch(server)})

        ips = sorted(resultdict.values())
        ips_set = set(ips)
        log.debug('\nNumber of servers: {}'.format(len(self.server_list)))
        log.debug("IP's :")
        for ip, ocorrencia in zip(ips_set, map(lambda x: ips.count(x), ips_set)):
            log.debug('{0} = {1} ocurrenc{2}'.format(ip if len(ip) > 0 else 'broken server',
                                                     ocorrencia, 'y' if ocorrencia == 1 else 'ies'))
        log.debug('\n')
        log.debug(resultdict)


def connected_to_internet(url='http://www.google.com/', timeout=5):
    """
    Check if it is connected to internet.

    :param url:
    :param timeout:
    :return:
    """
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        log.error("No internet connection available.")
    return False


def get_public_ip():
    """
    Get the public IP.

    :return:
    """
    public_ip = IPgetter().get_externalip()

    log.debug('public IP address is: {}'.format(str(public_ip)))
    return public_ip


def get_location_from_ip(ip, database):
    """
    Get location from public IP.

    :param ip:
    :param database:
    :return:
    """
    reader = None
    try:
        log.debug('database path: {}'.format(database))

        reader = geoip2.database.Reader(database)
        response = reader.city(ip)

        continent = response.continent.name
        country = response.country.name
        city = response.city.name
        cc = response.country.iso_code
        lat = response.location.latitude
        lng = response.location.longitude
        tz = response.location.time_zone
        state = response.subdivisions.most_specific.name

        return dict(continent=continent, country=country, state=state,
                    city=city, cc=cc, lat=lat, lng=lng, tz=tz)

    except OSError as e:
        log.exception(e)
    finally:
        if reader:
            reader.close()
