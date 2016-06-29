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

"""Display folders and messages.
"""

# Global Imports
import base64
# Django:
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext
from django.utils.translation import gettext_lazy as _

# Local
from mail_utils import serverLogin
from themesapp.shortcuts import render_to_response
from utils.config import WebpymailConfig
import msgactions

import hlimap

@login_required
def show_message(request, folder, uid):
    '''Show the message
    '''
    config = WebpymailConfig( request )

    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]

    # If it's a POST request
    if request.method == 'POST':
        try:
            msgactions.message_change( request, message )
        except hlimap.imapmessage.MessageNotFound:
            return redirect('message_list', folder=folder.url() )

    return render_to_response('mail/message_body.html',{'folder':folder,
        'message':message,
        'inline_img': config.getboolean('message', 'show_images_inline')},
        context_instance=RequestContext(request))

@login_required
def message_header( request, folder, uid ):
    '''Show the message header
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]

    return render_to_response('mail/message_header.html',{'folder':folder,
        'message':message},
        context_instance=RequestContext(request))

@login_required
def message_structure( request, folder, uid ):
    '''Show the message header
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]

    return render_to_response('mail/message_structure.html',{'folder':folder,
        'message':message},
        context_instance=RequestContext(request))

@login_required
def message_source( request, folder, uid ):
    '''Show the message header
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]
    # Assume that we have a single byte encoded string, this is because there
    # can be several different files with different encodings within the same
    # message.
    source = unicode(message.source(),'ISO-8859-1')

    return render_to_response('mail/message_source.html',{'folder':folder,
        'message':message, 'source': source },
        context_instance=RequestContext(request))

@login_required
def get_msg_part( request, folder, uid, part_number, inline = False ):
    '''Gets a message part.
    '''
    folder_name =  base64.urlsafe_b64decode(str(folder))

    M = serverLogin( request )
    folder = M[folder_name]
    message = folder[int(uid)]
    part = message.bodystructure.find_part(part_number)

    response = HttpResponse(content_type='%s/%s' % (part.media, part.media_subtype))

    if part.filename():
        filename = part.filename()
    else:
        filename = _('Unknown')

    if inline:
        response['Content-Disposition'] = 'inline; filename=%s' % filename
    else:
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

    if part.media.upper() == 'TEXT':
        response['Content-Type'] = '%s/%s; charset=%s' % (part.media, part.media_subtype, part.charset())
    else:
        response['Content-Type'] = '%s/%s' % (part.media, part.media_subtype)

    response.write( message.part(part) )
    response.close()

    return response

def get_msg_part_inline( request, folder, uid, part_number ):
    return get_msg_part( request, folder, uid, part_number, True )

def not_implemented(request):
    return render_to_response('mail/not_implemented.html',
        context_instance=RequestContext(request))

@login_required
def index(request):
    '''
    This is the main index, it reads the configuration file and
    redirects to the default view defined on the configuration
    file.
    '''
    config = WebpymailConfig( request )
    login_page = config.get('general','login_page')

    return HttpResponseRedirect(login_page)


