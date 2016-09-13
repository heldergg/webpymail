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

'''
Client side message sorting
'''


class SortProgError(Exception):
    pass


class Sorter:
    '''This class provides the comparison function for sorting messages
    according to the provided sort program.
    '''

    def __init__(self, message_list, message_dict, sort_program):
        '''
        @message_list - list to be sorted
        @message_dict - dict containing information about the messages in the
          form { MSG_UID: { msg info }, ... }
        @sort_program - tipple containing the sort program
        '''
        self.message_list = message_list
        self.message_dict = message_dict
        self.sort_program = sort_program

    def key_ARRIVAL(self, k):
        return self.message_dict[k]['data'].internaldate

    def key_CC(self, k):
        return ', '.join(self.message_dict[k]['data'].envelope.cc_short())

    def key_FROM(self, k):
        return ', '.join(self.message_dict[k]['data'].envelope.from_short())

    def key_DATE(self, k):
        return self.message_dict[k]['data'].envelope['env_date']

    def key_SIZE(self, k):
        return self.message_dict[k]['data'].size

    def key_SUBJECT(self, k):
        return self.message_dict[k]['data'].envelope['env_subject']

    def key_TO(self, k):
        return ', '.join(self.message_dict[k]['data'].envelope.to_short())

    def run(self):
        '''Read the sort program and executes it
        '''
        for keyword in reversed(self.sort_program):
            reverse = False
            if keyword[0] == '-':
                reverse = True
                keyword = keyword[1:]
            key_meth = getattr(self, 'key_%s' % keyword)
            self.message_list.sort(key=key_meth, reverse=reverse)
        return self.message_list
