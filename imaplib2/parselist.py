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

# Imports

import base64

# Attributes:

NOSELECT = r'\Noselect'
HASCHILDREN = r'\HasChildren'
HASNOCHILDREN = r'\HasNoChildren'


class Mailbox(object):
    def __init__(self, path, attributes, delimiter):
        self.path = path
        self.delimiter = delimiter
        self.attributes = attributes

        if delimiter:
            self.parts = tuple(path.split(delimiter))
        else:
            self.parts = (path,)

    # Attributes
    def test_attribute(self, attr):
        return attr in self.attributes

    def noselect(self):
        return self.test_attribute(NOSELECT)

    def has_children(self):
        return self.test_attribute(HASCHILDREN)

    # Operators
    def __eq__(self, y):
        '''Compares the mailbox name against a string or against another
        mailbox object.
        '''
        if isinstance(y, Mailbox):
            return self.__hash__() == y.__hash__()
        elif isinstance(y, str):
            mailbox = self.path
            if mailbox.upper() == 'INBOX':
                # INBOX should be case insensitive
                mailbox = 'INBOX'
                y = y.upper()
            return y == mailbox

    def __str__(self):
        if self.path.upper() == 'INBOX':
            # INBOX should be case insensitive
            return 'INBOX'
        return self.path

    # Mailbox name
    def level(self):
        return len(self.parts)-1

    def last_level(self):
        return self.parts[-1]

    def native(self):
        '''Return the mailbox in raw format using the delimiter
        understood by the server.
        '''
        return self.path

    def url(self):
        '''Return the folder name on a url safe way
        '''
        return base64.urlsafe_b64encode(self.path)

    def __repr__(self):
        return '<Mailbox instance "%s">' % (self.path)
