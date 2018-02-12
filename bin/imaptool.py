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

import os
import sys
import getopt
import getpass

from imaplib2 import D_SERVER, D_CLIENT
import imaplib2
from hlimap import ImapServer

#
# Utility functions
#


def server_login(host, port, ssl, user):
    """Login to the server
    """
    # Get the password
    passwd = getpass.getpass('Password: ')
    # Login to the server:
    M = ImapServer(host, port, ssl)
    M.login(user, passwd)

    return M

#
# Main
#


def usage():
    print('''Usage: %(script_name)s [command] [options]\n
    Commands:
        --list-mailboxes [mailbox patern]
                                List available mailboxes, accepts a regex as a
                                patern
        --mark-read <mailbox patern>
                                Mark the messages read, accepts a regex as a
                                patern

    Options:
        -o <imap server>
        --host <imap server>    (default: localhost) define the imap server to
                                connect to
        -u <user name>
        --user <user name>      (default: $USER) imap user name
        -s <type>
        --security <type>       (default: NONE) available options are: SSL,
                                NONE
        -p
        --port                  (default: 143) port to connect to, if SSL
                                security is used the default changes to 993

        -v
        --verbose               (default: False) show imap conversation

        -h --help               This help screen\n
    Notes:
        The mailbox patern is a regular expression. To match all the folders
        an empty string might be used.
    ''' % {'script_name': sys.argv[0]})


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hvo:u:s:p:',
                                   ['list-mailboxes=', 'mark-read=',
                                    'host=', 'user=', 'security=', 'port=',
                                    'help', 'verbose'])
    except getopt.GetoptError as err:
        print(str(err))
        print()
        usage()
        sys.exit(1)

    # Defaults
    user = os.getenv('USER')
    host = os.getenv('IMAPSERVER', 'localhost')
    port = 143
    security = 'NONE'

    # Optional args
    for o, a in opts:
        if o in ('-o', '--host'):
            host = a
        elif o in ('-u', '--user'):
            user = a
        elif o in ('-p', '--port'):
            try:
                port = int(a)
            except ValueError:
                print('The port number must be an integer')
                sys.exit(1)
        elif o in ('-s', '--security'):
            security = a.upper()
            if security not in ('TLS', 'SSL', 'NONE'):
                print('The security type must be TLS, or SSL or None.')
                sys.exit(2)
            if security == 'SSL' and port == 143:
                port = 993
        elif o in ('-v', '--verbose'):
            imaplib2.imapll.Debug = D_SERVER | D_CLIENT

    # Mandatory args
    for o, a in opts:
        if o == '--list-mailboxes':
            ssl = security == 'SSL'
            server = server_login(host, port, ssl, user)
            if not a:
                regex = '.*'
            else:
                regex = a
            print()
            print('The available folders are:')
            print()
            for folder in server.folder_tree.iter_match(regex):
                print(folder.path)
            sys.exit()

        elif o == '--mark-read':
            ssl = security == 'SSL'
            server = server_login(host, port, ssl, user)
            print('Going to mark messages read')
            if not a:
                regex = '.*'
            else:
                regex = a
            for folder in server.folder_tree.iter_match(regex):
                print('Marking folder: %s' % folder.path)
                folder.select()
                message_list = folder.message_list
                message_list.refresh_messages()
                raw_message_list = [uid for uid in
                                    message_list.flat_message_list]
                folder.set_flags(raw_message_list, r'\Seen')
            print('Done.')

            sys.exit()

    usage()
    sys.exit()
