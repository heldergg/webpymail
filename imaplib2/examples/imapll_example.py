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

'''Example usage of imaplib2.imapll
'''

import imaplib2.imapll

imaplib2.imapll.Debug = 3

if __name__ == '__main__':
    import getopt
    import getpass
    import sys
    import pprint

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

    M = imaplib2.imapll.IMAP4(host)

    pprint.pprint(M.send_command('LOGIN %s "%s"' % (USER, PASSWD)))

    pprint.pprint(M.send_command('LIST "INBOX" "*"'))

    pprint.pprint(M.send_command('LOGOUT'))
