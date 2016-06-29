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
so we are forced to do that our selfs.

We have also three different ways of displaying the message list:

    * Unsorted
    * Sorted
    * Threaded and sorted - naturaly if we use the

Because the library should have always the same capabilities no matter what
extensions the IMAP server might have we're forced to do, client side, all
the sorting and threading necessary if no extension is available.

The relation matrix is::

    T - thread capability
    S - sort capability
    D - Default search

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

Where the 'S' means server side and the 'C' client side.

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

# Utils

def flaten_nested( nested_list ):
    '''Flaten a nested list.
    '''
    for item in nested_list:
        if type(item) in (list, tuple):
            for sub_item in flaten_nested(item):
                yield sub_item
        else:
            yield item

def threaded_tree( nested_list, base_level = 0, parent = None ):
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

    def __next__(self):
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

class Sorter(object):
    '''This class profides the comparison function for sorting messages
    according to the provided sort program.
    '''
    def __init__( self, message_dict, sort_program ):
        '''
        @message_dict - dict containing information about the messages in the
          form { MSG_UID: { msg info }, ... }
        @sort_program - tipple containing the sort program
        '''
        self.message_dict = message_dict
        self.sort_program = sort_program

    def cmp_func( self, a, b, reverse ):
        if reverse:
            return cmp(b,a)
        else:
            return cmp(a,b)

    def cmp_ARRIVAL(self, a, b, reverse ):
        a = self.message_dict[a]['data'].internaldate
        b = self.message_dict[b]['data'].internaldate
        return self.cmp_func( a, b, reverse )

    def cmp_CC(self, a, b, reverse ):
        a = ', '.join( self.message_dict[a]['data'].envelope.cc_short() )
        b = ', '.join( self.message_dict[b]['data'].envelope.cc_short() )
        return self.cmp_func( a, b, reverse )

    def cmp_FROM(self, a, b, reverse ):
        a = ', '.join( self.message_dict[a]['data'].envelope.from_short() )
        b = ', '.join( self.message_dict[b]['data'].envelope.from_short() )
        return self.cmp_func( a, b, reverse )

    def cmp_DATE(self, a, b, reverse ):
        a = self.message_dict[a]['data'].envelope['env_date']
        b = self.message_dict[b]['data'].envelope['env_date']
        return self.cmp_func( a, b, reverse )

    def cmp_SIZE(self, a, b, reverse ):
        a = self.message_dict[a]['data'].size
        b = self.message_dict[b]['data'].size
        return self.cmp_func( a, b, reverse )

    def cmp_SUBJECT(self, a, b, reverse ):
        a = self.message_dict[a]['data'].envelope['env_subject']
        b = self.message_dict[b]['data'].envelope['env_subject']
        return self.cmp_func( a, b, reverse )

    def cmp_TO(self, a, b, reverse ):
        a = ', '.join( self.message_dict[a]['data'].envelope.to_short() )
        b = ', '.join( self.message_dict[b]['data'].envelope.to_short() )
        return self.cmp_func( a, b, reverse )

    def cmp_msg(self, a, b):
        '''Read the sort program, compare using the first criteria, if a and b
        are equal, uses the next criteria and so on. If the sort program is
        completely consumed it returns the last comparison.
        '''
        for keyword in self.sort_program:
            reverse = False
            if keyword[0] == '-':
                reverse = True
                keyword = keyword[1:]

            cmp_meth = getattr(self, 'cmp_%s' % keyword )
            cmp_val = cmp_meth( a, b, reverse )
            if cmp_val in (1,-1):
                return cmp_val
        return cmp_val

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
        self.search_capability = UNSORTED

        sort   = self._imap.has_capability('SORT')
        thread = (self._imap.has_capability('THREAD=ORDEREDSUBJECT') or
                  self._imap.has_capability('THREAD=REFERENCES'))
        if thread:
            self.search_capability = THREADED
        elif sort:
            self.search_capability = SORTED

        if thread:
            if self._imap.has_capability('THREAD=REFERENCES'):
                self.thread_alg = 'REFERENCES'
            else:
                self.thread_alg = 'ORDEREDSUBJECT'

        self.set_sort_program('-DATE')
        self.set_search_expression('ALL')

        # Message list options
        self.message_list = False
        self.refresh = True # Get the message list and their headers

        # Pagination options
        self.show_style = THREADED
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
    def set_search_expression(self, search_expression ):
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
        use = self.search_capability & self.show_style

        if use == THREADED:
            # We have the THREAD extension:
            message_list = self._imap.thread(self.thread_alg,
                'utf-8', self.search_expression)
        elif use == SORTED:
            # We have the SORT extension on the server:
            message_list = self._imap.sort(self.sort_string(),
                'utf-8', self.search_expression)
        else:
            # Just get the list.
            message_list = self._imap.search(self.search_expression)

        return message_list

    def refresh_messages(self):
        '''Gets the message ID or UID list.
        '''
        # TESTS:
        #self.search_capability = UNSORTED
        #self.show_style = SORTED

        # Obtain the message list
        message_list = self.get_message_list()

        use = self.search_capability & self.show_style
        if use != self.show_style:
            # We'll have to make the sorting and threading by hand when we
            # get the message's envelopes
            flat_message_list = message_list

            # TODO: This comment must be moved...
            # If we have to sort or thread on the client side, then
            # we have to get the envelope info from all the messages.
            #
            # PROBLEM: the THREAD command only sorts by date which is not
            # the best choice IMO, I may want a threaded list and have it
            # sorted by subject. So we have to do all the sorting client
            # side even if we have the SORT extension when the user wants a
            # threaded view. arrrgghhh! Even on this case it's good to have
            # the threading extension, since we can get the threaded list,
            # and only do the  sorting client side...
        else:
            if self.show_style == THREADED:
                flat_message_list = list(flaten_nested(message_list))
                self.root_list = []
            else:
                flat_message_list = message_list
                self.root_list = message_list

        self._number_messages = len(flat_message_list)

        # Create here a message dict in the form:
        #   { MSG_ID: { ... }, ... }
        message_dict = {}
        for msg_id in flat_message_list:
            if msg_id not in message_dict:
                message_dict[msg_id] = { 'children': [],
                                         'parent': None,
                                         'level': 0 }

        if self.show_style == THREADED:
            for msg_id, level, parent in threaded_tree(message_list):
                if level == 0:
                    self.root_list.append(msg_id)
                else:
                    if msg_id not in message_dict[parent]['children']:
                        message_dict[parent]['children'].append(msg_id)
                    message_dict[msg_id]['parent'] = parent
                    message_dict[msg_id]['level'] = level

        self.message_dict = message_dict
        self.flat_message_list = flat_message_list

        self.refresh = False

    def add_messages_range(self):
        '''Adds the current page of messages to the message_dict
        '''
        use = self.search_capability & self.show_style
        if use != self.show_style:
            # We have to sort and thread the messages by hand so we have to get
            # the header information from all the messages in the message list.
            message_list = list(self.flat_message_list)
            if message_list:
                for msg_id,msg_info in  self._imap.fetch(message_list,
                    '(ENVELOPE RFC822.SIZE FLAGS INTERNALDATE)').items():
                    self.message_dict[msg_id]['data'] = Message(
                        self.server, self.folder, msg_info )

                if self.show_style == SORTED:
                    # Sort the message list
                    sorter = Sorter(self.message_dict, self.sort_program )
                    message_list.sort(sorter.cmp_msg)

                self.flat_message_list = message_list
        else:
            # Get the message headers and construct
            if self.paginator.msg_per_page == -1:
                message_list = self.flat_message_list
            else:
                first_msg = ( self.paginator.current_page - 1 
                            ) * self.paginator.msg_per_page
                last_message = first_msg + self.paginator.msg_per_page - 1
                message_list = self.flat_message_list[first_msg:last_message+1]

            if message_list:
                for msg_id,msg_info in self._imap.fetch(message_list,
                            '(ENVELOPE RFC822.SIZE FLAGS INTERNALDATE)'
                                                       ).items():
                    self.message_dict[msg_id]['data'] = Message(
                        self.server, self.folder, msg_info )

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

        return Message( self.server, self.folder, msg_info )

    # Iterators
    def msg_iter_page(self):
        '''Iteract through the current range (page) of messages.
        '''
        if self.refresh:
            self.refresh_messages()
            self.add_messages_range()

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

        self.__bodystructure = None

    # Fetch messages
    def get_bodystructure(self):
        if not self.__bodystructure:
            self.__bodystructure = self._imap.fetch(self.uid,
                '(BODYSTRUCTURE)')[self.uid]['BODYSTRUCTURE']
        return self.__bodystructure
    bodystructure = property(get_bodystructure)

    def part(self, part, decode_html = False, decode_text = True ):
        '''Get a part from the server.

        The TEXT/PLAIN parts are decoded according to the BODYSTRUCTURE
        information. The TEXT/HTML parts aren't decoded by default.
        '''
        query = part.query()
        text = self.fetch(query)

        if part.body_fld_enc.upper() == 'BASE64':
            text = base64.b64decode(text )
        elif part.body_fld_enc.upper() == 'QUOTED-PRINTABLE':
            text = quopri.decodestring(text)

        if part.media.upper() == 'TEXT' and (decode_html or
            part.media_subtype.upper() != 'HTML') and decode_text:
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
