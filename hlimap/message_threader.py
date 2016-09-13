# WebPyMail - IMAP python/django web mail client
# Copyright (C) 2008 Helder Guerreiro

# This file is part of WebPyMail.
#
# WebPyMail is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WebPyMail is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

import collections
import datetime
import uuid


def transverse_thread(thread_messages, message_id):
    m = thread_messages
    for child in m[message_id]['children']:
        yield transverse_thread(thread_messages, child)
    if message_id != 'root':
        yield message_id


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
        self.thread_messages = collections.defaultdict(
                lambda: {'imap_id': None,
                         'parent': None,
                         'children': [],
                         'references': [],
                         'dummy': True,
                         'sent_date': datetime.datetime(1970, 1, 1, 0, 0, 0),
                         'subject': '', })

    def normalize_message_id(self, message_id):
        '''
        From the RFC:

        Implementations of the REFERENCES threading algorithm MUST
        normalize any msg-id in order to avoid false non-matches due
        to differences in quoting.

        For example, the msg-id
           <"01KF8JCEOCBS0045PS"@xxx.yyy.com>
        and the msg-id
           <01KF8JCEOCBS0045PS@xxx.yyy.com>
        MUST be interpreted as being the same Message ID.
        '''
        # This is the simplistic aproach for this problem
        # in the future a more robust soluction must be found
        if message_id:
            return message_id.replace('<', ''
                                      ).replace('>', ''
                                                ).replace('"', '')
        return ''

    def get_message_id(self, msg_id, message_id_list):
        '''Get the header "Message-ID:" from the message with UID or sequence
        number "msg_id".
        Each "Message-ID" must be normalized.
        '''
        message = self.message_dict[msg_id]['data']
        # Get the message_id header
        message_id = message.envelope['env_message_id']
        # Normalize the Message-ID:
        message_id = self.normalize_message_id(message_id)
        # If two or more messages have the same Message ID,
        # then only use that Message ID in the first (lowest
        # sequence number) message, and assign a unique
        # Message ID to each of the subsequent messages with
        # a duplicate of that Message ID.
        if message_id in message_id_list:
            message_id = str(uuid.uuid4()) + '+' + message_id
        message_id_list.append(message_id)
        return message_id

    def get_messages_references(self, msg_id):
        '''
        Retrive the references of the message, normalize them and store them
        '''
        message = self.message_dict[msg_id]['data']
        references = [self.normalize_message_id(message_id)
                      for message_id in message.references]
        return references

    def collect_message_information(self):
        message_id_list = []
        for msg_id in sorted(self.message_list):
            message_id = self.get_message_id(msg_id, message_id_list)
            references = self.get_messages_references(msg_id)
            self.thread_messages[message_id]['dummy'] = False
            self.thread_messages[message_id]['references'] = references
            self.thread_messages[message_id]['imap_id'] = msg_id
            self.thread_messages[message_id]['sent_date'] = (
                self.message_dict[msg_id]['data'].envelope['env_date'])
            self.thread_messages[message_id]['subject'] = (
                self.message_dict[msg_id]['data'].envelope['env_subject'])

    def find_family_from_references(self):
        '''
        Step (1)
        (A) Using the Message IDs in the message's references, link
        the corresponding messages (those whose Message-ID
        header line contains the given reference Message ID)
        together as parent/child.  Make the first reference the
        parent of the second (and the second a child of the
        first), the second the parent of the third (and the
        third a child of the second), etc.

        (B) Create a parent/child link between the last reference
        (or NIL if there are no references) and the current
        message.  If the current message already has a parent,
        it is probably the result of a truncated References
        header line, so break the current parent/child link
        before creating the new correct one.  As in step 1.A,
        do not create the parent/child link if creating that
        link would introduce a loop.  Note that if this message
        has no references, it will now have no parent.
        '''
        m = self.thread_messages
        for message_id in list(self.thread_messages.keys()):
            references = m[message_id]['references']
            for ref_1, ref_2 in zip(references, references[1:]):
                if ref_2 not in m[ref_1]['children']:
                    m[ref_1]['children'].append(ref_2)
                # Do not create a parent/child link if creating that
                # link would introduce a loop.  For example, before
                # making message A the parent of B, make sure that A
                # is not a descendent of B.
                if ref_1 not in m[ref_2]['children']:
                    m[ref_2]['parent'] = ref_1
            if references:
                m[message_id]['parent'] = references[-1]
                if message_id not in m[references[-1]]['children']:
                    m[references[-1]]['children'].append(message_id)
            # House keeping
            del m[message_id]['references']

    def create_root_message(self):
        '''
        Step (2)
        Gather together all of the messages that have no parents
        and make them all children (siblings of one another) of a
        dummy parent (the "root").  These messages constitute the
        first (head) message of the threads created thus far.
        '''
        m = self.thread_messages
        for message_id in list(self.thread_messages.keys()):
            if not m[message_id]['parent']:
                m[message_id]['parent'] = 'root'
                m['root']['children'].append(message_id)

    def prune_dummy_messages(self):
        '''
        Step (3)
        Prune dummy messages from the thread tree.  Traverse each
        thread under the root, and for each message:

            If it is a dummy message with NO children, delete it.

            If it is a dummy message with children, delete it, but
            promote its children to the current level.  In other
            words, splice them in with the dummy's siblings.

            Do not promote the children if doing so would make them
            children of the root, unless there is only one child.
        '''
        m = self.thread_messages
        for message_id in transverse_thread(self.thread_messages, 'root'):
            if m['message_id']['dummy']:
                if m['message_id']['children']:
                    if (m['message_id']['parent'] != 'root' or
                            len(m['message_id']['children']) == 1):
                        parent = m['message_id']['parent']
                        m[parent]['children'] += m['message_id']['children']
                        for child in m['message_id']['children']:
                            m[child]['parent'] = parent
                del m['message_id']
                continue

    def sort_messages(self):
        '''
        Step (4)
        Sort the messages under the root (top-level siblings only)
        by sent date as described in section 2.2.  In the case of a
        dummy message, sort its children by sent date and then use
        the first child for the top-level sort.
        '''
        def sort_by_date(thread_messages, message_id):
            def children_sort(message_id):
                if not thread_messages[message_id]['dummy']:
                    return thread_messages[message_id]['sent_date']
                sort_by_date(thread_messages, message_id)
                first_born = thread_messages[message_id]['children'][0]
                return thread_messages[first_born]['sent_date']
            if thread_messages[message_id]['children']:
                thread_messages[message_id]['children'].sort(key=children_sort)
        sort_by_date(self.thread_messages, 'root')

    def create_thread_list(self, message_id='root'):
        m = self.thread_messages
        message_list = []
        if not m[message_id]['dummy']:
            message_list.append(m[message_id]['imap_id'])
        if len(m[message_id]['children']) == 1:
            first_child = m[message_id]['children'][0]
            message_list += self.create_thread_list(first_child)
        elif len(m[message_id]['children']) > 1:
            for child in m[message_id]['children']:
                message_list.append(self.create_thread_list(child))
        return message_list

    def run(self):
        self.collect_message_information()
        # Step (1)
        self.find_family_from_references()
        # Step (2)
        self.create_root_message()
        # Step (3)
        self.prune_dummy_messages()
        # Step (4)
        self.sort_messages()
        # Step (5)

        print("#"*80)

        return self.create_thread_list('root')
