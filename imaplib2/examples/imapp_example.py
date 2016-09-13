#!/usr/bin/env python3

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

'''Example usage of imaplib2.imaplp
'''

import imaplib2.imapp

imaplib2.imapp.Debug = 3

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

    # Login establish the connection to the server
    M = imaplib2.imapp.IMAP4P(host, port=993, ssl=True)

    # Login to the server
    M.login(USER, PASSWD)

    print(M.list("INBOX", "*"))
    print(M.examine("INBOX"))
    print(M.examine("INBOX.Drafts"))
    print("Close: ", M.close())
    print()

    for folder in M.list("INBOX", "*"):
        print(folder)

    # Select a folder
    M.select('INBOX.Templates')

    ml = M.search_uid('ALL')

    a = M.fetch_uid(ml)
    print(len(list(a.keys())))

    message_str = '''Date: Mon, 7 Feb 1994 21:52:25 -0800 (PST)
From: example_01@example.org
Subject: afternoon meeting
To: example_02@example.org
Message-Id: <B27397-0100000@Blurdybloop.COM>
MIME-Version: 1.0
Content-Type: TEXT/PLAIN; CHARSET=US-ASCII

Hello Joe, do you think we can meet at 3:30 tomorrow?
'''
    for i in range(2):
        M.append('INBOX.Templates', message_str)
