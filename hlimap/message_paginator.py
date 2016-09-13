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
Message paginator
'''


class PaginatorError(Exception):
    pass


class Paginator(object):
    def __init__(self, msg_list):
        '''
        msg_list is an instance of hlimap.MessageList
        '''
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
            self.msg_list.refresh = True
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
