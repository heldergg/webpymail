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
# along with WebPyMail.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

"""Mail interface"""

# Global imports:
from django.conf.urls import url

from mailapp.views import folder, message_list, message, compose

folder_pat = r'FOLDER_(?P<folder>[A-Za-z0-9+.&%_=-]+)'

# Folders views:
urlpatterns = [
        url(r'^$', folder.show_folders_view, name='folder_list'),
        url(r'^' + folder_pat + r'/expand/$', folder.set_folder_expand,
            name='set_folder_expand'),
        url(r'^' + folder_pat + r'/collapse/$', folder.set_folder_collapse,
            name='set_folder_collapse'),
        ]

# Message list views
urlpatterns += [
        url(r'^' + folder_pat + r'/$', message_list.show_message_list_view,
            name='message_list'),
        ]

# Messages views:
urlpatterns += [
        url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/$', message.show_message,
            name='mailapp-message'),
        url(r'^' + folder_pat +
            r'/(?P<uid>[\d]+)/(?P<part_number>\d+(?:\.\d+)*)/$',
            message.get_msg_part, name='mailapp_message_part'),
        url(r'^' + folder_pat +
            r'/(?P<uid>[\d]+)/(?P<part_number>\d+(?:\.\d+)*)/inline/$',
            message.get_msg_part_inline, name='mailapp_mpart_inline'),
        url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/HEADER/$',
            message.message_header, name='mailapp_message_header'),
        url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/STRUCTURE/$',
            message.message_structure, name='mailapp_message_structure'),
        url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/SOURCE/$',
            message.message_source, name='mailapp_message_source'),
        ]

# Compose messages:
urlpatterns += [
    url(r'^compose/$',
        compose.new_message, name='mailapp_send_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/REPLY/$',
        compose.reply_message, name='mailapp_reply_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/REPLYALL/$',
        compose.reply_all_message, name='mailapp_reply_all_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/FORWARD_INLINE/$',
        compose.forward_message_inline, name='mailapp_forward_inline_message'),
    url(r'^' + folder_pat + r'/(?P<uid>[\d]+)/FORWARD/$',
        compose.forward_message, name='mailapp_forward_message'),
    ]
