# -*- coding: utf-8 -*-

# WebPyMail - IMAP python/django web mail client
# Copyright (C) 2008 Helder Guerreiro

## This file is part of WebPyMail.
##
## WebPyMail is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## WebPyMail is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with WebPyMail.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#
# $Id$
#

"""Display folders and associated actions
"""

# Imports:
# Python
import base64

# Django
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext

# Local
from mailapp.models import FoldersToExpand
from mail_utils import serverLogin
from themesapp.shortcuts import render_to_response
from utils.config import WebpymailConfig

##
# Views
##

@login_required
def show_folders_view(request):
    '''Show the account folders.
    '''
    # Login to the server:
    M = serverLogin( request )

    # Special folders
    # TODO: will get this from the user config
    M.set_special_folders('INBOX', 'INBOX.Drafts', 'INBOX.Templates')

    # Expandable folders
    expand_folders = request.user.folderstoexpand_set.all()
    if expand_folders:
        M.set_expand_list(*[ f.folder_name for f in expand_folders ])

    # Read the subscribed folder list:
    M.refresh_folders(subscribed=True)

    # Get the default identity
    config =  WebpymailConfig( request )
    identity_list = config.identities()
    default_address = identity_list[0]['mail_address']

    return render_to_response('mail/folder_list.html',
        {'server': M,
         'address': default_address },
        context_instance=RequestContext(request))

@login_required
def set_folder_expand(request, folder):
    folder_name =  base64.urlsafe_b64decode(str(folder))
    user = request.user

    folder_in_list = FoldersToExpand.objects.filter(user__exact=user,
          folder_name__exact = folder_name).count()

    if not folder_in_list:
        f = FoldersToExpand( user = user, folder_name = folder_name)
        f.save()

    return HttpResponseRedirect(reverse('folder_list'))

@login_required
def set_folder_collapse(request, folder):
    folder_name =  base64.urlsafe_b64decode(str(folder))
    user = request.user
    FoldersToExpand.objects.filter(user__exact=user,
          folder_name__exact = folder_name).delete()

    return HttpResponseRedirect(reverse('folder_list'))
