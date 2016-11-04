
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

"""Compose message forms
"""

# Import

import tempfile
import os
import re
import base64
from smtplib import SMTPRecipientsRefused, SMTPException

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_text
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.generic import View

# Local Imports
from utils.config import WebpymailConfig
from themesapp.shortcuts import render
from mailapp.models import Attachments
from mailapp.forms import ComposeMailForm
from mailapp.views.mail_utils import (serverLogin, send_mail,
                                      join_address_list, mail_addr_str,
                                      mail_addr_name_str, quote_wrap_lines,
                                      show_addrs, compose_rfc822)

# CONST

PLAIN = 1
MARKDOWN = 2

# RE
delete_re = re.compile(r'^delete_(\d+)$')


def imap_store(request, folder, message):
    '''
    Stores a message on an IMAP folder.
    '''
    server = serverLogin(request)
    folder = server[folder]
    folder.append(message.as_string())


class UploadFiles:
    '''
    File uploading manager
    '''

    def __init__(self, user, old_files=None, new_files=None):
        self.file_list = []
        self.user = user
        if new_files:
            # We have new uploaded files
            self.add_new_files(new_files)
        if old_files:
            # We have previously uploaded files
            self.add_old_files(old_files)

    def delete_id(self, id):
        for fl in self.file_list:
            if fl.id == id:
                # Remove file from the list:
                self.file_list.remove(fl)
                # Remove file from the file system
                os.remove(fl.temp_file)
                # Remove the file from the attachments table
                fl.delete()

    def delete(self):
        for fl in self.file_list:
            # Remove file from the file system
            os.remove(fl.temp_file)
            # Remove the file from the attachments table
            fl.delete()

        self.file_list = []

    def id_list(self):
        return [Xi.id for Xi in self.file_list]

    def add_old_files(self, file_list):
        '''
        @param file_list: a list of Attachments table ids.
        '''
        obj_lst = Attachments.objects.filter(user__exact=self.user
                                             ).in_bulk(file_list)
        self.file_list += [Xi for Xi in obj_lst.values()]

    def add_new_files(self, file_list):
        '''
        @param file_list: a file list as returned on request.FILES
        '''
        for a_file in file_list:
            # Create a temporary file
            fl = tempfile.mkstemp(suffix='.tmp', prefix='webpymail_',
                                  dir=settings.TEMPDIR)
            # Save the attachments to the temp file
            os.write(fl[0], a_file.read())
            os.close(fl[0])
            # Add a entry to the Attachments table:
            attachment = Attachments(
                                     user=self.user,
                                     temp_file=fl[1],
                                     filename=a_file.name,
                                     mime_type=a_file.content_type,
                                     sent=False)
            attachment.save()
            self.file_list.append(attachment)


class ComposeMail(View):
    '''
    Compose mail messages

    Context:

    page_title - self explanatory
    form - mail composing form
    uploaded_files - instance of UploadFiles or None
    '''
    page_title = _('New Message')
    uploaded_files = None

    def get_context_data(self):
        '''Build the message form context
        '''
        context = {}
        context['page_title'] = self.page_title
        context['uploaded_files'] = self.uploaded_files
        return context

    def get_message_data(self, request, context):
        message_data = {'text_format': 1,
                        'message_text': request.GET.get('text', ''),
                        'to_addr': request.GET.get('to_addr', ''),
                        'cc_addr': request.GET.get('cc_addr', ''),
                        'bcc_addr': request.GET.get('bcc_addr', ''),
                        'subject': request.GET.get('subject', ''),
                        'saved_files': request.GET.get('attachments', ''),
                        }
        return message_data

    def get_uploaded_files(self, request, message_data):
        uploaded_files = []
        attachments = message_data['saved_files']
        if attachments:
            uploaded_files = UploadFiles(request.user,
                                         old_files=attachments.split(','))
        return uploaded_files

    def post_uploaded_files(self, request, data):
        '''Create the UploadFiles object'''
        old_files = []
        if 'saved_files' in data:
            if data['saved_files']:
                old_files = data['saved_files'].split(',')
        file_list = request.FILES.getlist('attachment[]')
        return UploadFiles(request.user,
                           old_files=old_files,
                           new_files=file_list)

    def post_cancel(self, uploaded_files):
        # Delete files
        uploaded_files.delete()

    def post_delete_files(self, data, uploaded_files):
        '''Check if there is a request to delete files'''
        delete_files = False
        for key in data:
            match = delete_re.match(key)
            if match:
                id = int(match.groups()[0])
                uploaded_files.delete_id(id)
                delete_files = True
        return delete_files

    def post_saved_files(self, data, uploaded_files):
        '''Create an hidden field with the file list.
        In case the form does not validate, then the user doesn't have
        to upload it again'''
        data['saved_files'] = ','.join(['%d' % Xi
                                        for Xi in uploaded_files.id_list()])

    def post_form(self, request, data):
        return ComposeMailForm(data, request=request)

    # HTTP methods

    def get(self, request):
        print('Get')
        context = self.get_context_data()
        message_data = self.get_message_data(request, context)
        uploaded_files = self.get_uploaded_files(request, message_data)
        context['form'] = ComposeMailForm(initial=message_data,
                                          request=request)
        context['uploaded_files'] = uploaded_files
        return render(request,
                      'mail/send_message.html',
                      context)

    def post(self, request):
        print('Post')
        data = request.POST.copy()
        uploaded_files = self.post_uploaded_files(request, data)
        if 'cancel' in data:
            self.post_cancel(uploaded_files)
            return HttpResponseRedirect('/')
        other_action = self.post_delete_files(data, uploaded_files)
        self.post_saved_files(data, uploaded_files)
        if 'upload' in data:
            other_action = True
        form = self.post_form(request, data)
        if form.is_valid() and not other_action:
            pass
        else:
            # Return to the message composig view
            return render(request,
                          'mail/send_message.html',
                          {'form': form,
                           'uploaded_files': uploaded_files})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        print('Dispatch')
        return super(ComposeMail, self).dispatch(request, *args, **kwargs)


def send_message(request, text='', to_addr='', cc_addr='', bcc_addr='',
                 subject='', attachments='', headers={}):
    '''Generic send message view
    '''
    if request.method == 'POST':
        # Auxiliary data initialization
        new_data = request.POST.copy()
        other_action = False
        old_files = []
        if 'saved_files' in new_data:
            if new_data['saved_files']:
                old_files = new_data['saved_files'].split(',')
        file_list = request.FILES.getlist('attachment[]')
        uploaded_files = UploadFiles(request.user,
                                     old_files=old_files,
                                     new_files=file_list)

        # Check if there is a request to delete files
        for key in new_data:
            match = delete_re.match(key)
            if match:
                id = int(match.groups()[0])
                uploaded_files.delete_id(id)
                other_action = True

        # Check if the cancel button was pressed
        if 'cancel' in new_data:
            # Delete the files
            uploaded_files.delete()
            # return
            return HttpResponseRedirect('/')

        # create an hidden field with the file list.
        # In case the form does not validate, the user doesn't have
        # to upload it again
        new_data['saved_files'] = ','.join(['%d' % Xi
                                            for Xi in uploaded_files.id_list()]
                                           )
        user_profile = request.user.userprofile
        form = ComposeMailForm(new_data, request=request)
        if 'upload' in new_data:
            other_action = True

        if form.is_valid() and not other_action:
            # Read the posted data
            form_data = form.cleaned_data

            subject = form_data['subject']
            from_addr = form_data['from_addr']

            to_addr = join_address_list(form_data['to_addr'])
            cc_addr = join_address_list(form_data['cc_addr'])
            bcc_addr = join_address_list(form_data['bcc_addr'])

            text_format = form_data['text_format']
            message_text = form_data['message_text'].encode('utf-8')

            config = WebpymailConfig(request)

            # Create html message
            if text_format == MARKDOWN and HAS_MARKDOWN:
                md = markdown.Markdown(output_format='HTML')
                message_html = md.convert(smart_text(message_text))
                css = config.get('message', 'css')
                # TODO: use a template to get the html and insert the css
                message_html = ('<html>\n<style>%s</style>'
                                '<body>\n%s\n</body>\n</html>' %
                                (css, message_html))
            else:
                message_html = None

            # Create the RFC822 message
            # NOTE: the current relevant RFC is RFC 5322, maybe this function
            # name should be changed to reflect this, maybe it shouldn't be
            # named after the RFC!
            message = compose_rfc822(from_addr, to_addr, cc_addr, bcc_addr,
                                     subject, message_text, message_html,
                                     uploaded_files, headers)

            # Post the message to the SMTP server
            try:
                host = config.get('smtp', 'host')
                port = config.getint('smtp', 'port')
                user = config.get('smtp', 'user')
                passwd = config.get('smtp', 'passwd')
                security = config.get('smtp', 'security').upper()
                use_imap_auth = config.getboolean('smtp', 'use_imap_auth')

                if use_imap_auth:
                    user = request.session['username']
                    passwd = request.session['password']

                send_mail(message, host, port, user, passwd, security)
            except SMTPRecipientsRefused as detail:
                error_message = ''.join(
                    ['<p>%s' % escape(detail.recipients[Xi][1])
                     for Xi in detail.recipients])
                return render(request, 'mail/send_message.html',
                              {'form': form,
                               'server_error': error_message,
                               'uploaded_files': uploaded_files})
            except SMTPException as detail:
                return render(request, 'mail/send_message.html',
                              {'form': form,
                               'server_error': '<p>%s' % detail,
                               'uploaded_files': uploaded_files})
            except Exception as detail:
                error_message = '<p>%s' % detail
                return render(request, 'mail/send_message.html',
                              {'form': form,
                               'server_error': error_message,
                               'uploaded_files': uploaded_files})

            # Store the message on the sent folder
            imap_store(request, user_profile.sent_folder, message)

            # Delete the temporary files
            uploaded_files.delete()

            return HttpResponseRedirect('/')
        else:
            # Return to the message composig view
            return render(request,
                          'mail/send_message.html',
                          {'form': form,
                           'uploaded_files': uploaded_files})

    else:
        # Create the intial message
        initial = {'text_format': 1,
                   'message_text': text,
                   'to_addr': to_addr,
                   'cc_addr': cc_addr,
                   'bcc_addr': bcc_addr,
                   'subject': subject,
                   'saved_files': attachments}

        if attachments:
            uploaded_files = UploadFiles(request.user,
                                         old_files=attachments.split(','))
        else:
            uploaded_files = []

        form = ComposeMailForm(initial=initial,
                               request=request)
        return render(request,
                      'mail/send_message.html',
                      {'form': form,
                       'uploaded_files': uploaded_files})


@login_required
def new_message(request):
    if request.method == 'GET':
        to_addr = request.GET.get('to_addr', '')
        cc_addr = request.GET.get('cc_addr', '')
        bcc_addr = request.GET.get('bcc_addr', '')
        subject = request.GET.get('subject', '')
    else:
        to_addr = ''
        cc_addr = ''
        bcc_addr = ''
        subject = ''
    return send_message(request, to_addr=to_addr, cc_addr=cc_addr,
                        bcc_addr=bcc_addr, subject=subject)


@login_required
def reply_message(request, folder, uid):
    '''Reply to a message'''
    # Get the message
    server = serverLogin(request)
    folder_name = base64.urlsafe_b64decode(str(folder))
    folder = server[folder_name]
    message = folder[int(uid)]
    headers = {}

    # References header:
    message_id = message.envelope['env_message_id']
    references = message.references.copy()
    if message_id:
        references.append(message_id)
    headers['References'] = ' '.join(references)

    # In-Reply-To header:
    headers['In-Reply-To'] = message_id

    if request.method == 'GET':
        # Extract the relevant headers
        to_addr = mail_addr_str(message.envelope['env_from'][0])
        subject = _('Re: ') + message.envelope['env_subject']

        # Extract the message text
        text = ''
        for part in message.bodystructure.serial_message():
            if part.is_text() and part.is_plain():
                text += message.part(part)

        # Quote the message
        text = quote_wrap_lines(text)
        text = _('On %s, %s wrote:\n%s' % (
                    message.envelope['env_date'],
                    mail_addr_name_str(message.envelope['env_from'][0]),
                    text)
                 )

        # Invoque the compose message form
        return send_message(request, text=text, to_addr=to_addr,
                            subject=subject, headers=headers)
    else:
        # Invoque the compose message form
        return send_message(request, headers=headers)


@login_required
def reply_all_message(request, folder, uid):
    '''Reply to a message'''
    # Get the message we're replying to
    server = serverLogin(request)
    folder_name = base64.urlsafe_b64decode(str(folder))
    folder = server[folder_name]
    message = folder[int(uid)]
    headers = {}

    # References header:
    message_id = message.envelope['env_message_id']
    references = message.references.copy()
    if message_id:
        references.append(message_id)
    headers['References'] = ' '.join(references)

    # In-Reply-To header:
    headers['In-Reply-To'] = message_id

    if request.method == 'GET':
        # Extract the relevant headers
        to_addr = mail_addr_str(message.envelope['env_from'][0])
        cc_addr = join_address_list(message.envelope['env_to'] +
                                    message.envelope['env_cc'])
        subject = _('Re: ') + message.envelope['env_subject']

        # Extract the message text
        text = ''
        for part in message.bodystructure.serial_message():
            if part.is_text() and part.is_plain():
                text += message.part(part)

        # Quote the message
        text = quote_wrap_lines(text)
        text = _('On %s, %s wrote:\n%s' % (
                    message.envelope['env_date'],
                    mail_addr_name_str(message.envelope['env_from'][0]),
                    text)
                 )

        # Invoque the compose message form
        return send_message(request, text=text, to_addr=to_addr,
                            cc_addr=cc_addr, subject=subject)
    else:
        # Invoque the compose message form
        return send_message(request, headers=headers)


@login_required
def forward_message(request, folder, uid):
    '''Reply to a message'''
    # Get the message
    M = serverLogin(request)
    folder_name = base64.urlsafe_b64decode(str(folder))
    folder = M[folder_name]
    message = folder[int(uid)]
    headers = {}

    # References header:
    message_id = message.envelope['env_message_id']
    references = message.references.copy()
    if message_id:
        references.append(message_id)
    headers['References'] = ' '.join(references)

    # In-Reply-To header:
    headers['In-Reply-To'] = message_id

    if request.method == 'GET':
        # Extract the relevant headers
        subject = _('Fwd: ') + message.envelope['env_subject']

        # Create a temporary file
        fl = tempfile.mkstemp(suffix='.tmp', prefix='webpymail_',
                              dir=settings.TEMPDIR)

        # Save message source to a file
        os.write(fl[0], bytes(message.source(), 'utf-8'))
        os.close(fl[0])

        # Add a entry to the Attachments table:
        attachment = Attachments(
            user=request.user,
            temp_file=fl[1],
            filename='attached_message',
            mime_type='MESSAGE/RFC822',
            sent=False)
        attachment.save()

        return send_message(request, subject=subject,
                            attachments='%d' % attachment.id)
    else:
        # Invoque the compose message form
        return send_message(request, headers=headers)


@login_required
def forward_message_inline(request, folder, uid):
    '''Reply to a message'''
    def message_header(message):
        text = ''
        text += show_addrs(_('From'), message.envelope['env_from'],
                           _('Unknown'))
        text += show_addrs(_('To'), message.envelope['env_to'], _('-'))
        text += show_addrs(_('Cc'), message.envelope['env_cc'], _('-'))
        text += (_('Date: ') +
                 message.envelope['env_date'].strftime('%Y-%m-%d %H:%M') +
                 '\n')
        text += _('Subject: ') + message.envelope['env_subject'] + '\n\n'

        return text

    # Get the message
    M = serverLogin(request)
    folder_name = base64.urlsafe_b64decode(str(folder))
    folder = M[folder_name]
    message = folder[int(uid)]
    headers = {}

    # References header:
    message_id = message.envelope['env_message_id']
    references = message.references.copy()
    if message_id:
        references.append(message_id)
    headers['References'] = ' '.join(references)

    # In-Reply-To header:
    headers['In-Reply-To'] = message_id
    if request.method == 'GET':
        # Extract the relevant headers
        subject = _('Fwd: ') + message.envelope['env_subject']

        # Extract the message text
        text = ''
        text += '\n\n' + _('Forwarded Message').center(40, '-') + '\n'
        text += message_header(message)

        for part in message.bodystructure.serial_message():
            if part.is_text() and part.is_plain() and not part.is_attachment():
                text += message.part(part)

            if part.is_encapsulated():
                if part.is_start():
                    text += ('\n\n' +
                             _('Encapsuplated Message').center(40, '-') +
                             '\n')
                    text += message_header(part)
                else:
                    text += ('\n' +
                             _('End Encapsuplated Message').center(40, '-') +
                             '\n')
        text += '\n' + _('End Forwarded Message').center(40, '-') + '\n'

        # Extract the message attachments
        attach_list = []
        for part in message.bodystructure.serial_message():
            if part.is_attachment() and not part.is_encapsulated():
                # Create a temporary file
                fl = tempfile.mkstemp(suffix='.tmp', prefix='webpymail_',
                                      dir=settings.TEMPDIR)

                # Save message source to a file
                os.write(fl[0], message.part(part, decode_text=False))
                os.close(fl[0])

                # Add a entry to the Attachments table:
                attachment = Attachments(
                    user=request.user,
                    temp_file=fl[1],
                    filename=(part.filename()
                              if part.filename() else
                              _('Unknown')),
                    mime_type='%s/%s' % (part.media, part.media_subtype),
                    content_desc=(part.body_fld_desc
                                  if part.body_fld_desc else
                                  ''),
                    content_id=part.body_fld_id if part.body_fld_id else '',
                    show_inline=part.body_fld_dsp[0].upper() != 'ATTACHMENT',
                    sent=False)
                attachment.save()
                attach_list.append(attachment.id)

        return send_message(request, subject=subject, text=text,
                            attachments=','.join(['%d' % Xi
                                                  for Xi in attach_list])
                            )
    else:
        # Invoque the compose message form
        return send_message(request, headers=headers)
