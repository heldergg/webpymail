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

'''This module provides a single class that is used to register status
responses from the server.
'''


class InfoLog(list):
    '''Collects and manages the information and warnings issued by the server in
    the form of status responses.

    This can be overriden or completly replaced provided that the interface
    stays the same.

    By default it stores the last 10 entries, this can be defined while
    creating the instance.
    '''

    def __init__(self, max_entries=10, *args):
        '''Creates a new InfoLog list.

        @param max_entries: number of entries to keep
        @type max_entries: integer
        '''
        self.max_entries = max_entries
        self.action_list = []

        list.__init__(self, *args)

    def addEntry(self, type, data):
        '''Adds a new log entry.

        @param type: the type of the entry (warning, error, info, etc)
        @type  type: string

        @param data: any python object.
        '''
        type = type.upper()
        if len(self) == self.max_entries:
            del self[0]
        self.append({'type': type, 'data': data})

        for action in self.action_list:
            if action['type'] == type:
                action['action'](type, data)

    def addAction(self, type, action):
        '''A callback action can be defined. Every time a new log is made
        the callback action will be executed.

        @param type: the type that will trigger the action
        @param action: a python callable, the arguments used will be
        (type, data).
        '''
        self.action_list.append({'type': type, 'action': action})


if __name__ == '__main__':
    a = InfoLog()

    def printAA(type, data):
        print('Type: ', type)
        print('Data: :', data)

    a.addAction('AA', printAA)
    for i in range(20):
        a.addEntry('AA', 'AAAAA %d' % i)

    print(a)

    for i in a:
        print(i['data'])
