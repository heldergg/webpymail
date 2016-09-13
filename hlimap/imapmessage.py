# -*- coding: utf-8 -*-

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

'''High Level IMAP Lib - message handling

This module is part of the hlimap lib.

Notes
=====

At this level we have the problem of getting and presenting the message list,
and the message it self.

Message List
------------

Since IMAP has several extentions, the search for the messages can be made
on three different ways:

    * Unsorted, using the SEARCH command - standard
    * Sorted, using the SORT command - extension
    * Threaded, using the THREAD command - extension

To confuse things even further, the THREAD command does not sort the messages,
so we are forced to do that ourselves.

We have also three different ways of displaying the message list:

    * Unsorted
    * Sorted
    * Threaded and sorted

Because the library should have always the same capabilities no matter what
extensions the IMAP server might have we're forced to do, client side, all
the sorting and threading necessary if no extension is available.

The relation matrix is:

    Capabilities:
        T - thread capability
        S - sort capability
        D - Default search

    C - Client side
    S - Server side

    +---------------+-----------------+-----------------+
    | Display mode  |           Capabilities            |
    +---------------+-----------------+-----------------+
    |               | D               | S D             |
    +---------------+-----------------+-----------------+
    | Threaded      | C THREAD C SORT | C THREAD C SORT |
    +---------------+-----------------+-----------------+
    | Sorted        | C SORT          | S SORT          |
    +---------------+-----------------+-----------------+
    | Unsorted      | S SEARCH        | S SEARCH        |
    +---------------+-----------------+-----------------+

    +---------------+-----------------+-----------------+
    | Display mode  |           Capabilities            |
    +---------------+-----------------+-----------------+
    |               | T S D           | T D             |
    +---------------+-----------------+-----------------+
    | Threaded      | S THREAD C SORT | S THREAD C SORT |
    +---------------+-----------------+-----------------+
    | Sorted        | S SORT          | C SORT          |
    +---------------+-----------------+-----------------+
    | Unsorted      | S SEARCH        | S SEARCH        |
    +---------------+-----------------+-----------------+

Please note the THREAD command response is in the form:

    S: * THREAD (2)(3 6 (4 23)(44 7 96))

    -- 2
    -- 3
        \-- 6
            |-- 4
            |   \-- 23
            \-- 44
                \-- 7
                    \-- 96
'''

# Imports
import base64
import quopri

from imaplib2.parsefetch import Single

from .message_threader import Threader
from .message_sorter import Sorter, SortProgError
from .message_paginator import Paginator

# Utils


def flaten_nested(nested_list):
    '''Flaten a nested list.
    '''
    for item in nested_list:
        if type(item) in (list, tuple):
            for sub_item in flaten_nested(item):
                yield sub_item
        else:
            yield item


def threaded_tree(nested_list, base_level=0, parent=None):
    '''Analyses the tree, returns child depth (level)
    '''
    level = base_level
    for item in nested_list:
        if type(item) in (list, tuple):
            for sub_item in threaded_tree(item, level, parent):
                yield sub_item
        else:
            yield item, level, parent
            level += 1
            parent = item

# Exceptions:


class MessageNotFound(Exception):
    pass

# Constants:

SORT_KEYS = ('ARRIVAL', 'CC', 'DATE', 'FROM', 'SIZE', 'SUBJECT', 'TO')

UNSORTED = 1
SORTED = 2
THREADED = 3

# System flags
DELETED = r'\Deleted'
SEEN = r'\Seen'
ANSWERED = r'\Answered'
FLAGGED = r'\Flagged'
DRAFT = r'\Draft'
RECENT = r'\Recent'


class MessageList(object):
    def __init__(self, server, folder):
        '''
        @param server: ImapServer instance
        @param folder: Folder instance this message list is associated with
        @param threaded: should we show a threaded message list?
        '''
        self._imap = server._imap
        self.server = server
        self.folder = folder
        # Sort capabilities:
        sort = self._imap.has_capability('SORT')
        thread = (self._imap.has_capability('THREAD=ORDEREDSUBJECT') or
                  self._imap.has_capability('THREAD=REFERENCES'))
        self.search_capability = [UNSORTED]
        if thread:
            self.search_capability.append(THREADED)
        if sort:
            self.search_capability.append(SORTED)
        if thread:
            if self._imap.has_capability('THREAD=REFERENCES'):
                self.thread_alg = 'REFERENCES'
            else:
                self.thread_alg = 'ORDEREDSUBJECT'
        # Sort program setup
        self.set_sort_program('-DATE')
        self.set_search_expression('ALL')
        # Message list options
        self.refresh = True  # Get the message list and their headers
        self.flat_message_list = []
        # Pagination options
        self.show_style = SORTED
        self._number_messages = None
        self.paginator = Paginator(self)

    # Sort program:
    def sort_string(self):
        sort_program = ''
        reverse = False
        for keyword in self.sort_program:
            keyword = keyword.upper()
            if keyword[0] == '-':
                keyword = keyword[1:]
                reverse = True
            else:
                reverse = False
            if reverse:
                sort_program += 'REVERSE '
            sort_program += '%s ' % keyword
        sort_program = '(%s)' % sort_program.strip()
        return sort_program

    def test_sort_program(self, sort_list):
        for keyword in sort_list:
            if keyword[0] == '-':
                keyword = keyword[1:]
            if keyword.upper() not in SORT_KEYS:
                raise SortProgError('Sort key unknown.')
        return True

    def set_sort_program(self, *sort_list):
        '''Define the sort program to use, the available keywords are:
        ARRIVAL, CC, DATE, FROM, SIZE, SUBJECT, TO

        Any of this words can be perpended by a - meaning reverse order.
        '''
        self.test_sort_program(sort_list)
        self.sort_program = sort_list

    # Search expression:
    def set_search_expression(self, search_expression):
        self.search_expression = search_expression

    # Display options
    def set_threaded(self):
        self.show_style = THREADED

    def set_sorted(self):
        self.show_style = SORTED

    # Information retrieval
    def _get_number_messages(self):
        if self.search_expression.upper() == 'ALL':
            self._number_messages = self.folder.status['MESSAGES']
        if self._number_messages is None:
            self.refresh_messages()
        return self._number_messages
    number_messages = property(_get_number_messages)

    def have_messages(self):
        return bool(self.number_messages)

    def get_message_list(self):
        '''
        Get a message list of message IDs or UIDs if available, using the
        following method:
        +--------------+--------+--------+------+--------+--------+--------+
        | Show         | SORT   | THREAD | SORT | THREAD | SORT   | THREAD |
        +--------------+--------+--------+------+--------+--------+--------+
        | Capability   | None   | None   | SORT | SORT   | THREAD | THREAD |
        +--------------+--------+--------+------+--------+--------+--------+
        | IMAP command | SEARCH | SEARCH | SORT | SORT   | SEARCH | THREAD |
        +--------------+--------+--------+------+--------+--------+--------+
        '''
        if THREADED in self.search_capability and self.show_style == THREADED:
            # We have the THREAD extension:
            message_list = self._imap.thread(self.thread_alg,
                                             'utf-8', self.search_expression)
            flat_message_list = list(flaten_nested(message_list))
        elif SORTED in self.search_capability:
            # We have the SORT extension on the server:
            message_list = self._imap.sort(self.sort_string(),
                                           'utf-8', self.search_expression)
            flat_message_list = message_list[:]
        else:
            # Just get the list.
            message_list = list(self._imap.search(self.search_expression))
            flat_message_list = message_list[:]
        return message_list, flat_message_list

    def create_message_dict(self, flat_message_list):
        '''Create here a message dict in the form:
           { MSG_ID: { ... }, ... }
        the MSG_ID is the imap UID ou ID of each message'''
        # Empty message dict
        message_dict = {}
        for msg_id in flat_message_list:
            if msg_id not in message_dict:
                message_dict[msg_id] = {'children': [],
                                        'parent': None,
                                        'level': 0}
        return message_dict

    def update_message_dict(self, message_list, message_dict):
        for msg_id, level, parent in threaded_tree(message_list):
            if msg_id not in message_dict:
                continue
            if level > 0:
                if parent in message_dict:
                    if msg_id not in message_dict[parent]['children']:
                        message_dict[parent]['children'].append(msg_id)
                message_dict[msg_id]['parent'] = parent
                message_dict[msg_id]['level'] = level
                message_dict[msg_id]['data'].level = level
        return message_dict

    def create_message_objects(self, flat_message_list, message_dict):
        if flat_message_list:
            for msg_id, msg_info in self._imap.fetch(flat_message_list,
                                                     ('(ENVELOPE RFC822.SIZE '
                                                      'FLAGS INTERNALDATE '
                                                      'BODY.PEEK[HEADER.FIELDS'
                                                      ' (REFERENCES)])')
                                                     ).items():
                message_dict[msg_id]['data'] = Message(
                    self.server, self.folder, msg_info)
        return message_dict

    def paginate(self, flat_message_list):
        if self.paginator.msg_per_page == -1:
            message_list = self.flat_message_list
        else:
            first_msg = (self.paginator.current_page - 1
                         ) * self.paginator.msg_per_page
            last_message = first_msg + self.paginator.msg_per_page - 1
            message_list = flat_message_list[first_msg:last_message+1]
        return message_list

    def refresh_messages(self):
        '''
        This method retrieves the message list. This is a bit complicated
        since the path taken to get the message list changes according
        to the server capabilities and the display mode the user wants to
        view:

        +--------------+--------+--------+------+--------+--------+--------+
        | Show         | SORT   | THREAD | SORT | THREAD | SORT   | THREAD |
        +--------------+--------+--------+------+--------+--------+--------+
        | Capability   | None   | None   | SORT | SORT   | THREAD | THREAD |
        +--------------+--------+--------+------+--------+--------+--------+
        | IMAP command | SEARCH | SEARCH | SORT | SORT   | SEARCH | THREAD |
        +--------------+--------+--------+------+--------+--------+--------+
        |              |      1 |      1 |    1 |      1 |      1 |      1 |
        |              |      2 |      2 |    5 |      5 |      2 |      2 |
        |              |      4 |      3 |    2 |      2 |      4 |      5 |
        |              |      5 |      5 |      |      3 |      5 |        |
        +--------------+--------+--------+------+--------+--------+--------+

        Steps:
            1 - get the message list
            2 - get the necessary info to sort the messages
            3 - do the threading client side
            4 - do a client side sort
            5 - paginate

        Notes:

        - The pagination is the last step except if the server has the SORT
        capability. If it has this capability we only need to retrieve the
        message header information for a page of messages instead of getting
        the information for all messages on the search program (ALL by
        default).
        '''
        # Obtain the message list
        message_list, flat_message_list = self.get_message_list()
        # Set the number of message present in the folder according to the
        # current search expression
        self._number_messages = len(flat_message_list)
        # Paginate now if we have SORT or THREAD capability, this way we don't
        # have to retrieve message headers to all messages returned by the
        # search program
        if (SORTED in self.search_capability or
           THREADED in self.search_capability):
            flat_message_list = self.paginate(flat_message_list)
            if (not(self.show_style == THREADED and
               THREADED in self.search_capability)):
                message_list = list(flat_message_list)
        # Create the message dictionary
        message_dict = self.create_message_dict(flat_message_list)
        # Get message's header information
        message_dict = self.create_message_objects(flat_message_list,
                                                   message_dict)
        # Client side threading
        if (self.show_style == THREADED and
           THREADED not in self.search_capability):
            message_list = Threader(message_list, message_dict).run()
            flat_message_list = list(flaten_nested(message_list))
        # Client side sorting
        if SORTED not in self.search_capability and self.show_style == SORTED:
            message_list = Sorter(
                    message_list,
                    message_dict,
                    self.sort_program).run()
            flat_message_list = list(message_list)
        # Update the message dict with the level information of the
        # thread level of each message and each message children
        if self.show_style == THREADED:
            message_dict = self.update_message_dict(message_list, message_dict)
            # TODO: Sort the threads according to the defined program unless
            # we have the sort extension
        # House keeping
        self.message_dict = message_dict
        self.flat_message_list = flat_message_list
        self.refresh = False

    # Handle a request for a single message:
    def get_message(self, message_id):
        '''Gets a _single_ message from the server
        '''
        # We need to get the msg envelope to initialize the
        # Message object
        try:
            msg_info = self._imap.fetch(message_id,
                                        ('(ENVELOPE RFC822.SIZE FLAGS '
                                         'INTERNALDATE BODY.PEEK[HEADER.FIELDS'
                                         ' (REFERENCES)])'))[message_id]
        except KeyError:
            raise MessageNotFound('%s message not found' % message_id)
        return Message(self.server, self.folder, msg_info)

    # Iterators
    def msg_iter_page(self):
        '''Iteract through the current range (page) of messages.
        '''
        if self.refresh:
            self.refresh_messages()
        if self.paginator.msg_per_page == -1:
            message_list = self.flat_message_list
        elif len(self.flat_message_list) > self.paginator.msg_per_page:
            first_msg = (self.paginator.current_page - 1
                         ) * self.paginator.msg_per_page
            last_message = first_msg + self.paginator.msg_per_page - 1
            message_list = self.flat_message_list[first_msg:last_message+1]
        else:
            # If we're using the SORT extention the flat_message_list is
            # truncated early in order to avoid downloading the message
            # information for all the messages in the folder.
            message_list = self.flat_message_list
        for msg_id in message_list:
            yield self.message_dict[msg_id]['data']

    # Special methods
    def __repr__(self):
        return '<MessageList instance in folder "%s">' % (self.folder.name)


class Message(object):
    def __init__(self, server, folder, msg_info):
        self.server = server
        self._imap = server._imap
        self.folder = folder
        # Problem: msg_info carries lots of information that can vary quite a
        # bit. We could query this information from within this class, but then
        # we would have to query the IMAP server once for each message this is
        # not efficient.
        # It seems that collecting this info is arbitrary and will force the
        # user to alter this class if new information is necessary.
        # This should be open.
        # TODO: Create a manager to collect this information on demand or
        # to store it if it is available in msg_info when creating a new
        # Message instance.
        self.envelope = msg_info['ENVELOPE']
        self.size = msg_info['RFC822.SIZE']
        self.uid = msg_info['UID']
        self.id = msg_info['ID']
        self.get_flags(msg_info['FLAGS'])
        self.internaldate = msg_info['INTERNALDATE']
        self.references = self.get_references(msg_info)
        self.level = 0  # Thread level
        self.__bodystructure = None

    # References
    def get_references(self, msg_info):
        ref_list = []
        if 'BODY.PEEK[HEADER.FIELDS (REFERENCES)]' in msg_info:
            ref_list = msg_info['BODY.PEEK[HEADER.FIELDS (REFERENCES)]']
            ref_list = ref_list.split('References:')
            if len(ref_list) < 2:
                return []
            return [ref.strip(' \r\n\t')
                    for ref in msg_info['BODY.PEEK[HEADER.FIELDS '
                                        '(REFERENCES)]'].split(
                    'References:')[1].split() if ref.strip(' \r\n\t')]
        return []

    # Fetch messages
    def get_bodystructure(self):
        if not self.__bodystructure:
            bodystructure = self._imap.fetch(self.uid, '(BODYSTRUCTURE)')
            self.__bodystructure = bodystructure[self.uid]['BODYSTRUCTURE']
        return self.__bodystructure
    bodystructure = property(get_bodystructure)

    def part(self, part, decode_text=True):
        '''Get a part from the server.

        The TEXT/PLAIN and TEXT/HTML parts are decoded according to the
        BODYSTRUCTURE information.
        '''
        query = part.query()
        text = self.fetch(query)

        if part.body_fld_enc.upper() == 'BASE64':
            text = base64.b64decode(text)
        elif part.body_fld_enc.upper() == 'QUOTED-PRINTABLE':
            text = quopri.decodestring(text)

        if (part.media.upper() == 'TEXT' and
            part.media_subtype.upper() in ('HTML', 'PLAIN') and
            decode_text and
                not isinstance(text, str)):
            try:
                return str(text, part.charset())
            except (UnicodeDecodeError, LookupError):
                # Some times the messages have the wrong encoding, for
                # instance PHPMailer sends a text/plain with charset utf-8
                # but the actual contents are iso-8859-1. Here we can try
                # to guess the encoding on a case by case basis.
                try:
                    return str(text, 'iso-8859-1')
                except:
                    raise
        return text

    def fetch(self, query):
        '''Returns the fetch response for the query
        '''
        return self._imap.fetch(self.uid, query)[self.uid][query]

    def source(self):
        '''Returns the message source, untreated.
        '''
        return self.fetch('BODY[]')

    def part_header(self, part=None):
        '''Get a part header from the server.
        '''
        if part:
            query = 'BODY[%s.HEADER]'
        else:
            query = 'BODY[HEADER]'

        text = self._imap.fetch(self.uid, query)[self.uid][query]

        return text

    # Search
    def search_fld_id(self, body_fld_id):
        '''
        Search the message parts for a single part with id body_fld_id
        '''
        for part in self.bodystructure.serial_message():
            if isinstance(part, Single):
                part_fld_id = part.body_fld_id
                if part_fld_id:
                    part_fld_id = part_fld_id.replace('<', '').replace('>', '')
                if part_fld_id == body_fld_id:
                    return part
        return None

    # Flags:
    def get_flags(self, flags):
        self.seen = SEEN in flags
        self.deleted = DELETED in flags
        self.answered = ANSWERED in flags
        self.flagged = FLAGGED in flags
        self.draft = DRAFT in flags
        self.recent = RECENT in flags

    def set_flags(self, *args):
        self._imap.store(self.uid, '+FLAGS', args)
        if self._imap.expunged():
            # The message might have been expunged
            if self._imap.is_expunged(self.id):
                # The message no longer exists
                self._imap.reset_expunged()
                raise MessageNotFound('The message was expunged,'
                                      ' Google IMAP does this...')

        self.get_flags(self._imap.sstatus['fetch_response'][self.uid]['FLAGS'])

    def reset_flags(self, *args):
        self._imap.store(self.uid, '-FLAGS', args)
        self.get_flags(self._imap.sstatus['fetch_response'][self.uid]['FLAGS'])

    # Special methods
    def __repr__(self):
        return '<Message instance in folder "%s", uid "%s">' % (
            self.folder.name, self.uid)
