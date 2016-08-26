# -*- coding: utf-8 -*-

# hlimap - High level IMAP library
# Copyright (C) 2008 Helder Guerreiro

## This file is part of hlimap.
##
## hlimap is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## hlimap is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

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
import quopri, base64
from imaplib2.parsefetch import Single

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

def threaded_tree(nested_list, base_level = 0, parent = None):
    '''Analyses the tree
    '''
    level = base_level

    for item in nested_list:
        if type(item) in (list, tuple):
            for sub_item in threaded_tree(item, level, parent ):
                yield sub_item
        else:
            yield item, level, parent
            level += 1
            parent = item

# Exceptions:

class SortProgError(Exception): pass
class PaginatorError(Exception): pass
class MessageNotFound(Exception): pass
class NotImplementedYet(Exception): pass

# Constants:

SORT_KEYS = ( 'ARRIVAL', 'CC', 'DATE', 'FROM', 'SIZE', 'SUBJECT', 'TO' )

THREADED = 7
SORTED   = 3
UNSORTED = 1

# System flags
DELETED = r'\Deleted'
SEEN = r'\Seen'
ANSWERED = r'\Answered'
FLAGGED = r'\Flagged'
DRAFT = r'\Draft'
RECENT = r'\Recent'

class Paginator(object):
    def __init__(self, msg_list):
        self.msg_list = msg_list
        # self.msg_per_page = -1 => ALL MESSAGES
        self.msg_per_page = 50
        self.__page = 1

    def _get_max_page(self):
        if self.msg_per_page == -1:
            return 1
        if self.msg_list.number_messages % self.msg_per_page:
            return 1 + self.msg_list.number_messages // self.msg_per_page
        else:
            return self.msg_list.number_messages // self.msg_per_page
    max_page = property(_get_max_page)

    def _set_page(self, page):
        if page < 1:
            page = 1
        elif page > self.max_page:
            page = self.max_page
        if self.__page != page:
            self.refresh = True
        self.__page = page

    def _get_page(self):
        if self.msg_per_page == -1:
            return 1
        return self.__page
    current_page = property(_get_page, _set_page)

    def has_next_page(self):
        return self.current_page < self.max_page

    def next(self):
        if self.has_next_page():
            return self.current_page + 1
        else:
            return 1

    def has_previous_page(self):
        return self.current_page > 1

    def previous(self):
        if self.has_previous_page():
            return self.current_page - 1
        else:
            return self.max_page

    def is_last(self):
        return self.current_page == self.max_page

    def is_not_last(self):
        return self.current_page < self.max_page

    def last(self):
        return self.max_page

    def is_first(self):
        return self.current_page == 1

    def is_not_first(self):
        return self.current_page > 1

class Threader:
    '''Implements the client side REFERENCES threading algorithm defined in
    RFC 5256 - https://tools.ietf.org/html/rfc5256
    This is an adaptation of the threading algorithm by Jamie Zawinski which
    was included in Netscape News and Mail 2.0 and 3.0:
    https://www.jwz.org/doc/threading.html
    '''
    def __init__(self, message_list, message_dict):
        self.message_list = message_list
        self.message_dict = message_dict
    def run(self):
        return self.message_list

class Sorter:
    '''This class provides the comparison function for sorting messages
    according to the provided sort program.
    '''
    def __init__(self, message_list, message_dict, sort_program, threaded):
        '''
        @message_list - list to be sorted
        @message_dict - dict containing information about the messages in the
          form { MSG_UID: { msg info }, ... }
        @sort_program - tipple containing the sort program
        '''
        self.message_list = message_list
        self.message_dict = message_dict
        self.sort_program = sort_program
        self.threaded     = threaded

    def key_ARRIVAL(self, k):
        return self.message_dict[k]['data'].internaldate

    def key_CC(self, k):
        return ', '.join( self.message_dict[k]['data'].envelope.cc_short() )

    def key_FROM(self, k):
        return ', '.join( self.message_dict[k]['data'].envelope.from_short() )

    def key_DATE(self, k):
        return self.message_dict[k]['data'].envelope['env_date']

    def key_SIZE(self, k):
        return self.message_dict[k]['data'].size

    def key_SUBJECT(self, k):
        return self.message_dict[k]['data'].envelope['env_subject']

    def key_TO(self, k):
        return ', '.join( self.message_dict[k]['data'].envelope.to_short() )

    def run(self):
        '''Read the sort program and executes it
        '''
        if not self.threaded:
            for keyword in reversed(self.sort_program):
                reverse = False
                if keyword[0] == '-':
                    reverse = True
                    keyword = keyword[1:]
                key_meth = getattr(self, 'key_%s' % keyword )
                self.message_list.sort(key=key_meth,reverse=reverse)
        return self.message_list

class MessageList(object):
    def __init__(self, server, folder, threaded=False):
        '''
        @param server: ImapServer instance
        @param folder: Folder instance this message list is associated with
        @param threaded: should we show a threaded message list?
        '''
        self._imap  = server._imap
        self.server = server
        self.folder = folder
        # Sort capabilities:
        sort   = self._imap.has_capability('SORT')
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
        self.refresh = True # Get the message list and their headers
        self.flat_message_list = []
        # Pagination options
        self.show_style = THREADED if threaded else SORTED
        self._number_messages = None
        self.paginator = Paginator(self)

        # REMOVE THIS! This is to test the client side sorting and threading
        self.show_style = THREADED
        self.search_capability = [UNSORTED, THREADED]

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

    def test_sort_program(self, sort_list ):
        for keyword in sort_list:
            if keyword[0] == '-':
                keyword = keyword[1:]
            if keyword.upper() not in SORT_KEYS:
                raise SortProgError('Sort key unknown.')
        return True

    def set_sort_program(self, *sort_list ):
        '''Define the sort program to use, the available keywords are:
        ARRIVAL, CC, DATE, FROM, SIZE, SUBJECT, TO

        Any of this words can be perpended by a - meaning reverse order.
        '''
        self.test_sort_program( sort_list )
        self.sort_program = sort_list

    # Search expression:
    def set_search_expression(self, search_expression):
        self.search_expression = search_expression

    # Information retrieval
    def _get_number_messages(self):
        if self._number_messages == None:
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
            flat_message_list = message_list
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
                message_dict[msg_id] = { 'children': [],
                                         'parent': None,
                                         'level': 0 }
        return message_dict

    def update_message_dict(self, message_list, message_dict):
        for msg_id, level, parent in threaded_tree(message_list):
            if level>0:
                if msg_id not in message_dict[parent]['children']:
                    message_dict[parent]['children'].append(msg_id)
                message_dict[msg_id]['parent'] = parent
                message_dict[msg_id]['level'] = level
                message_dict[msg_id]['data'].level = level
        return message_dict

    def create_message_objects(self, flat_message_list, message_dict):
        if flat_message_list:
            for msg_id,msg_info in self._imap.fetch(flat_message_list,
                '(ENVELOPE RFC822.SIZE FLAGS INTERNALDATE BODY[HEADER.FIELDS (REFERENCES)])').items():
                message_dict[msg_id]['data'] = Message(
                    self.server, self.folder, msg_info )
        return message_dict

    def paginate(self, flat_message_list):
        if self.paginator.msg_per_page == -1:
            message_list = self.flat_message_list
        else:
            first_msg = ( self.paginator.current_page - 1
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
        |              |      4 |      3 |    2 |      2 |      4 |      4 |
        |              |      5 |      4 |      |      3 |      5 |      5 |
        |              |        |      5 |      |        |        |        |
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
        # Paginate now if we have SORT capability, this way we don't have to
        # retrieve message headers to all messages returned by the search
        # program
        if SORTED in self.search_capability:
            message_list = self.paginate(flat_message_list)
            flat_message_list = list(message_list)
        # Create the message dictionary
        message_dict = self.create_message_dict(flat_message_list)
        # Get message's header information
        message_dict = self.create_message_objects(flat_message_list, message_dict)
        # Client side threading
        if self.show_style==THREADED and THREADED not in self.search_capability:
            message_list = Threader(message_list, message_dict).run()
        # Client side sorting
        if SORTED not in self.search_capability:
            message_list = Sorter(
                    message_list,
                    message_dict,
                    self.sort_program,
                    self.show_style == THREADED).run()
        # Update the message dict with the level information of about the
        # thread level of each message
        if self.show_style==THREADED:
            message_dict = self.update_message_dict(message_list, message_dict)
        # House keeping
        self.message_dict = message_dict
        self.flat_message_list = flat_message_list
        self.refresh = False

    # Handle a request for a single message:
    def get_message(self, message_id ):
        '''Gets a _single_ message from the server
        '''
        # We need to get the msg envelope to initialize the
        # Message object
        try:
            msg_info = self._imap.fetch(message_id,
                '(ENVELOPE RFC822.SIZE FLAGS INTERNALDATE)')[message_id]
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
        else:
            first_msg = ( self.paginator.current_page - 1
                        ) * self.paginator.msg_per_page
            last_message = first_msg + self.paginator.msg_per_page - 1
            message_list = self.flat_message_list[first_msg:last_message+1]
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
        self.envelope = msg_info['ENVELOPE']
        self.size = msg_info['RFC822.SIZE']
        self.uid = msg_info['UID']
        self.id = msg_info['ID']
        self.get_flags( msg_info['FLAGS'] )
        self.internaldate = msg_info['INTERNALDATE']
        self.level = 0 # Thread level
        self.__bodystructure = None

    # Fetch messages
    def get_bodystructure(self):
        if not self.__bodystructure:
            self.__bodystructure = self._imap.fetch(self.uid,
                '(BODYSTRUCTURE)')[self.uid]['BODYSTRUCTURE']
        return self.__bodystructure
    bodystructure = property(get_bodystructure)

    def part(self, part, decode_text = True ):
        '''Get a part from the server.

        The TEXT/PLAIN and TEXT/HTML parts are decoded according to the
        BODYSTRUCTURE information.
        '''
        query = part.query()
        text = self.fetch(query)

        if part.body_fld_enc.upper() == 'BASE64':
            text = base64.b64decode(text )
        elif part.body_fld_enc.upper() == 'QUOTED-PRINTABLE':
            text = quopri.decodestring(text)

        if (part.media.upper() == 'TEXT' and
            part.media_subtype.upper() in  ('HTML', 'PLAIN') and
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

    def fetch(self, query ):
        '''Returns the fetch response for the query
        '''
        return self._imap.fetch(self.uid,query)[self.uid][query]

    def source(self):
        '''Returns the message source, untreated.
        '''
        return self.fetch('BODY[]')

    def part_header(self, part = None):
        '''Get a part header from the server.
        '''
        if part:
            query = 'BODY[%s.HEADER]'
        else:
            query = 'BODY[HEADER]'

        text = self._imap.fetch(self.uid,query)[self.uid][query]

        return text

    # Search
    def search_fld_id(self, body_fld_id):
        '''
        Search the message parts for a single part with id body_fld_id
        '''
        for part in self.bodystructure.serial_message():
            if isinstance(part,Single):
                part_fld_id = part.body_fld_id
                if part_fld_id:
                    part_fld_id = part_fld_id.replace('<','').replace('>','')
                if part_fld_id == body_fld_id:
                    return part
        return None

    # Flags:
    def get_flags(self, flags):
        self.seen = SEEN in flags
        self.deleted = DELETED in flags
        self.answered = ANSWERED  in flags
        self.flagged = FLAGGED in flags
        self.draft = DRAFT in flags
        self.recent = RECENT in flags

    def set_flags(self, *args ):
        self._imap.store(self.uid, '+FLAGS', args)
        if self._imap.expunged():
           # The message might have been expunged
           if self._imap.is_expunged(self.id):
               # The message no longer exists
               self._imap.reset_expunged()
               raise MessageNotFound('The message was expunged,'
                    ' Google IMAP does this...')

        self.get_flags(self._imap.sstatus['fetch_response'][self.uid]['FLAGS'])

    def reset_flags(self, *args ):
        self._imap.store(self.uid, '-FLAGS', args)
        self.get_flags(self._imap.sstatus['fetch_response'][self.uid]['FLAGS'])

    # Special methods
    def __repr__(self):
        return '<Message instance in folder "%s", uid "%s">' % (
            self.folder.name, self.uid)
