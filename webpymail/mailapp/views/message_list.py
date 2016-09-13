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

"""Display message lists and associated actions
"""

# Imports:
# Standard lib
import base64

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Local
from mailapp.forms import MessageActionForm
from .mail_utils import serverLogin
from themesapp.shortcuts import render
from utils.config import WebpymailConfig
from . import msgactions
from hlimap.imapmessage import SORT_KEYS

#
# Views
#


@login_required
def show_message_list_view(request, folder=settings.DEFAULT_FOLDER):
    '''Show the selected Folder message list.
    '''
    M = serverLogin(request)
    folder_name = base64.urlsafe_b64decode(str(folder))
    folder = M[folder_name]
    message_list = folder.message_list

    # Set the search criteria:
    search_criteria = 'ALL'
    message_list.set_search_expression(search_criteria)

    # Handle GET queries
    query = request.GET.copy()

    flag = request.GET.get('flag', None)
    if flag:
        search_criteria = 'KEYWORD %s' % flag

    show_style = request.GET.get('show_style', 'sorted')
    if show_style.upper() == 'THREADED':
        message_list.set_threaded()

    sort_order = request.GET.get('sort_order', 'DATE').upper()
    sort = request.GET.get('sort', 'DESCENDING').upper()
    if sort == 'DESCENDING':
        sort = '-'
    else:
        sort = ''
    if sort_order in SORT_KEYS:
        message_list.set_sort_program('%s%s' % (sort, sort_order))

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = request.GET.get('page', 1)
        if page == 'all':
            message_list.paginator.msg_per_page = -1
        page = 1
    if 'page' in query:
        query.pop('page')

    # Pagination
    message_list.paginator.msg_per_page = 40
    message_list.paginator.current_page = page

    # Message action form
    message_list.refresh_messages()  # Necessary to get the flat_message_list
    raw_message_list = [(uid, uid) for uid in message_list.flat_message_list]
    form = MessageActionForm(data={}, message_list=raw_message_list, server=M)

    # If it's a POST request
    if request.method == 'POST':
        msgactions.batch_change(request, folder, raw_message_list)
        # TODO: When setting message flags the MessageList's messages objects
        # are not updated, so we have to refresh the messages to reflect the
        # changes in the message list. This should not be necessary, the set
        # and reset flags method in the Folder objects should update the
        # message information, saving this way a refresh_messages call.
        message_list.refresh_messages()

    # Get the default identity
    config = WebpymailConfig(request)
    identity_list = config.identities()
    default_address = identity_list[0]['mail_address']

    # Show the message list
    return render(request,  'mail/message_list.html', {
            'folder': folder,
            'address': default_address,
            'paginator': folder.paginator(),
            'query': query,
            'form': form})
