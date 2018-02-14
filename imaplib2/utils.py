# -*- coding: utf-8 -*-

# imaplib2 python module, meant to be a replacement to the python default
# imaplib module
# Copyright (C) 2008 Helder Guerreiro

# This file is part of imaplib2.
#
# imaplib2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# imaplib2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

'''Utility functions for the imaplib2 module.
'''

# Global imports
import time
import datetime
import re
from email.header import decode_header
from email.errors import HeaderParseError


def to_bytes(s, encoding='utf-8'):
    if isinstance(s, str):
        s = bytes(s, encoding)
    return s

# Utility functions


def getUnicodeHeader(header):
    '''Returns an unicode string with the content of the
    header string.
    '''
    if not header:
        return ''
    # Decode the header:
    header_list = []
    try:
        decoded_header = decode_header(header)
    except HeaderParseError:
        # This is necessary to deal with bug 22
        try:
            decoded_header = decode_header(header.replace('?==?', '?= =?'))
        except:
            # If unable to decode the header, return it unchanged
            return header
    for header in decoded_header:
        if not header[1]:
            codec = 'iso-8859-1'
        else:
            codec = header[1]
        if isinstance(header[0], str):
            # "decode_header" returns str if no charset is defined
            # imapll converts the bytes string to str using utf-8 encoding
            # if the server only returns ascii we should be OK in converting
            # back to bytes this way:
            txt = bytes(header[0], 'utf-8')
        else:
            # "decode_header" returns bytes if a charset is found:
            txt = header[0]
        try:
            text = str(txt, codec)
        except:
            try:
                text = str(txt, 'iso-8859-1')
            except:
                raise
        header_list.append(text)
    return ' '.join(header_list)


def getUnicodeMailAddr(address_list):
    '''Return an address list with the mail addresses
    '''
    if not isinstance(address_list, list):
        return []

    # Verify the encoding:
    return [(unquote(getUnicodeHeader(Xi[0])), '%s@%s' % (Xi[2], Xi[3]))
            for Xi in address_list]


def Int2AP(num):
    """Convert integer to A-P string representation."""
    val = ''
    AP = 'ABCDEFGHIJKLMNOP'
    num = int(abs(num))
    while num:
        num, mod = divmod(num, 16)
        val = AP[mod:mod+1] + val
    return val


def makeTagged(tagged):
    '''Composes a string with the tagged response'''
    return ('\nStatus: %(status)s\nMessage: %(message)s\nCommand: %(command)s'
            % tagged)


def unquote(string):
    if len(string) > 0:
        if string[0] == string[-1] == '"' or \
           string[0] == string[-1] == '\'':
            return string[1:-1]
    return string

Mon2num = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
           'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

InternalDate = re.compile(
    r'(?P<day>[ 0123][0-9])-(?P<mon>[A-Z][a-z][a-z])-'
    r'(?P<year>[0-9][0-9][0-9][0-9])'
    r' (?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9])'
    r' (?P<zonen>[-+])(?P<zoneh>[0-9][0-9])(?P<zonem>[0-9][0-9])'
    )

EnvelopeDate = re.compile(r'(?:(?P<week_day>[A-Z][a-z][a-z]), )?'
                          r'(?P<day>[ \d][0-9]?) '
                          r'(?P<month>[A-Z][a-z][a-z]) '
                          r'(?P<year>[0-9][0-9][0-9][0-9]) '
                          r'(?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):'
                          r'(?P<sec>[0-9][0-9]) '
                          r'(?P<zonen>[-+])(?P<zoneh>[0-9][0-9])'
                          r'(?P<zonem>[0-9][0-9]).*'
                          )


def envelopedate2datetime(resp):
    '''Convert an envelope date to tuple

    Returns Python time module tuple.
    '''
    if not resp:
        return datetime.datetime.fromtimestamp(0)

    mo = EnvelopeDate.match(resp)

    if not mo:
        return datetime.datetime.fromtimestamp(0)

    try:
        mon = Mon2num[mo.group('month')]
    except:
        return datetime.datetime.fromtimestamp(0)
    zonen = mo.group('zonen')

    day = int(mo.group('day'))
    year = int(mo.group('year'))
    hour = int(mo.group('hour'))
    min = int(mo.group('min'))
    sec = int(mo.group('sec'))
    zoneh = int(mo.group('zoneh'))
    zonem = int(mo.group('zonem'))

    # INTERNALDATE timezone must be subtracted to get UT

    zone = (zoneh*60 + zonem)*60
    if zonen == '-':
        zone = -zone

    tt = (year, mon, day, hour, min, sec, -1, -1, -1)

    try:
        utc = time.mktime(tt)
    except:
        return datetime.datetime.fromtimestamp(0)

    # Following is necessary because the time module has no 'mkgmtime'.
    # 'mktime' assumes arg in local timezone, so adds timezone/altzone.

    lt = time.localtime(utc)
    if time.daylight and lt[-1]:
        zone = zone + time.altzone
    else:
        zone = zone + time.timezone

    return datetime.datetime.fromtimestamp(utc - zone)


def internaldate2datetime(resp):
    """Convert IMAP4 INTERNALDATE to UT.

    Returns Python datetime.datetime object
    """
    mo = InternalDate.match(resp)
    if not mo:
        return None

    mon = Mon2num[mo.group('mon')]
    zonen = mo.group('zonen')

    day = int(mo.group('day'))
    year = int(mo.group('year'))
    hour = int(mo.group('hour'))
    min = int(mo.group('min'))
    sec = int(mo.group('sec'))
    zoneh = int(mo.group('zoneh'))
    zonem = int(mo.group('zonem'))

    # INTERNALDATE timezone must be subtracted to get UT

    zone = (zoneh*60 + zonem)*60
    if zonen == '-':
        zone = -zone

    tt = (year, mon, day, hour, min, sec, -1, -1, -1)

    utc = time.mktime(tt)

    # Following is necessary because the time module has no 'mkgmtime'.
    # 'mktime' assumes arg in local timezone, so adds timezone/altzone.

    lt = time.localtime(utc)
    if time.daylight and lt[-1]:
        zone = zone + time.altzone
    else:
        zone = zone + time.timezone

    return datetime.datetime.fromtimestamp(utc - zone)


def list_to_int(msg_list):
    '''Converts a message list, nested or not, to int.
    '''
    return [list_to_int(msg_id)
                if isinstance(msg_id, list) else
                    int(msg_id)
                        for msg_id in msg_list]


def shrink_fetch_list(msg_list):
    '''Shrinks the message list to use on the fetch command, consecutive msg_list
    numbers will be converted to first:last.

    @param msg_list: a list of message numbers or uids
    @type msg_list: list

    @return: a list with the shrinked msg_list
    '''
    tmp = []
    msg_list = list(msg_list)
    if not msg_list:
        return []

    msg_list.sort()
    last = msg_list[0]
    anchor = 0

    for msgn in msg_list[1:]:
        if (last + 1) == msgn and not anchor:
            anchor = last
        elif anchor:
            if (last + 1) != msgn:
                if (anchor + 1) != last:
                    tmp.append('%d:%d' % (anchor, last))
                else:
                    tmp.append('%d' % anchor)
                    tmp.append('%d' % last)
                anchor = 0
        else:
            tmp.append(last)

        last = msgn

    if anchor:
        if (anchor + 1) != last:
            tmp.append('%d:%d' % (anchor, last))
        else:
            tmp.append('%d' % anchor)
            tmp.append('%d' % last)
    else:
        tmp.append('%d' % last)

    return tmp

#
# Classes
#


class ContinuationRequests(list):
    '''Class to be used with the continuation requests made by the server.
    '''

    def push(self, data):
        self.insert(0, data)

    def pop(self, challenge):
        try:
            response = list.pop(self)
            try:
                response = response(challenge)
            except TypeError:
                pass
            return response
        except IndexError:  # Empty list
            return '*'

    def clear(self):
        del self[:]
        # try:
        #     while True: list.pop(self)
        # except: pass
