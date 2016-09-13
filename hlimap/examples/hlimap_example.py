#!/usr/bin/env python3

# hlimap - High level IMAP library
# Copyright (C) 2008 Helder Guerreiro

# This file is part of hlimap.
#
# hlimap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hlimap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

'''Example usage of hlimap
'''

#
# hlimap test for the notes app
#

import imaplib2.imapll
import hlimap

D_SERVER = 1        #: Debug responses from the server
D_CLIENT = 2        #: Debug data sent by the client
D_RESPONSE = 4      #: Debug obtained response

imaplib2.imapll.Debug = D_SERVER | D_CLIENT

if __name__ == '__main__':
    import getopt
    import getpass
    import sys

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'd:s:')
    except getopt.error as val:
        optlist, args = (), ()

    if not args:
        args = ('',)

    host = args[0]

    USER = getpass.getuser()
    PASSWD = getpass.getpass('IMAP password for %s on %s: ' %
                             (USER, host or "localhost"))

    # Connect to the server
    server = hlimap.ImapServer(host, port=993, ssl=True)
    server.login(USER, PASSWD)

    # Configure
    server.set_special_folders('INBOX',
                               'INBOX.Drafts',
                               'INBOX.Templates',
                               'INBOX.Trash')

    # Folder operations
    server.folder_iterator = 'iter_match'
    server.folder_tree.regex_filter = r'^INBOX\.N.*'

    # List the folder tree
    for folder in server:
        print('##' * folder.level(), '%s' % folder)

    # List the contents of a folder
    INBOX = server['INBOX']
    INBOX.message_list.paginator.msg_per_page = -1  # All messages
    INBOX.message_list.paginator.msg_per_page = 50
    for msg in INBOX:
        print(msg.envelope['env_date'], msg.envelope['env_subject'])
