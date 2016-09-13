# -*- coding: utf-8 -*-

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

'''Forms used on the mailapp application
'''

# Imports

from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings

import re

from utils.config import WebpymailConfig
from .multifile import MultiFileField

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# Mail form exceptions


class MAILFORMERROR (Exception):
    pass

# Custom Fields

# Regular expressions:

single_mail_address = r'([_a-zA-Z0-9-]+(?:\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+' +\
                      r'(?:\.[a-zA-Z0-9-]+)*\.(?:(?:[0-9]{1,3})|' + \
                      r'(?:[a-zA-Z]{2,3})|(?:aero|coop|info|museum|name)))'

mail_address = r'(?:[\'"](.*?)[\'"] +)?<?' + single_mail_address + r'>?'

email_list_re = re.compile(mail_address)

teste_emails_re = re.compile(r'^ *(' + mail_address + r'[ ,;]*)+$')


class MultiEmailField(forms.Field):
    def clean(self, value):
        '''
        Clean up the address list provided by the user.

        The address list should have the mail addresses sepparated by commas,
        spaces or ';'.

        Each address may be represented by:

            DQUOTE | QUOTE + Name + DQUOTE | QUOTE <mail_address>
        or  <mail_address>
        or  mail_address

        Examples: "Test Address" <test@example.com>
                  'Test Address' <test@example.com>
                  <test@example.com>
                  test@example.com

        The return addresses will have the format:
            [('Name','address'), ... ]
        '''
        # Make sure that:
        #   i) The addresses are valid
        #  ii) There is at least one address
        if not teste_emails_re.match(value):
            if not self.required and not value:
                return ''
            elif not self.required and value:
                raise forms.ValidationError(_('Invalid mail address.'))
            raise forms.ValidationError(_('Enter at least one valid email '
                                          'address.'))

        # Get all the addresses as a list
        emails = email_list_re.findall(value)

        if len(emails) > settings.MAXADDRESSES:
            raise forms.ValidationError('%s %s' %
                                        (_('Exceeded the maximum number of '
                                           'addresses by:'),
                                         len(emails) - settings.MAXADDRESSES))

        return emails


class MultyChecksum(forms.Field):
    '''Field used to hold a list checksums of the uploaded files
    '''
    widget = forms.HiddenInput()
    required = False

    def clean(self, value):
        # FIXME: Lacking validation here
        return value.split(',')


# Forms

class ComposeMailForm(forms.Form):
    def __init__(self, *args, **kwargs):

        request = kwargs.pop('request')
        super(ComposeMailForm, self).__init__(*args, **kwargs)

        # Populate the identity choices
        config = WebpymailConfig(request)
        identity_list = config.identities()
        from_list = []
        for identity in identity_list:
            if identity['user_name'] and identity['mail_address']:
                addr = '"%s" <%s>' % (identity['user_name'],
                                      identity['mail_address'])
            elif identity['mail_address']:
                addr = '<%s>' % identity['mail_address']
            else:
                continue

            from_list.append((addr, addr))

        if not from_list:
            addr = '<%s@%s>' % (request.session['username'],
                                request.session['host'])
            from_list = [(addr, addr)]
        self.fields['from_addr'].choices = from_list

    from_addr = forms.ChoiceField(
        label=_('From'),
        help_text="<div class=\"helptext\">%s</div>" % _('Your email address'),
        required=True
        )

    to_addr = MultiEmailField(
        label=_('To'),
        help_text=('<div class=\"helptext\">%s</div>' %
                   _('To addresses, separated by commas')),
        widget=forms.TextInput(attrs={'size': settings.SINGLELINELEN}),
        required=True
        )

    cc_addr = MultiEmailField(
        label=_('Cc'),
        help_text='<div class=\"helptext\">%s</div>' %
        _('Carbon Copy addresses, separated by commas'),
        widget=forms.TextInput(attrs={'size': settings.SINGLELINELEN}),
        required=False
        )

    bcc_addr = MultiEmailField(
        label=_('Bcc'),
        help_text='<div class=\"helptext\">%s</div>' %
        _('Blind Carbon Copy addresses, separated by commas'),
        widget=forms.TextInput(attrs={'size': settings.SINGLELINELEN}),
        required=False
        )

    if HAS_MARKDOWN:
        text_format = forms.TypedChoiceField(
                coerce=int,
                choices=((1, _('Plain')), (2, _('Markdown'))),
                label=_('Format'), )
    else:
        text_format = forms.IntegerField(initial=1,
                                         widget=forms.HiddenInput())

    subject = forms.CharField(
        max_length=100,
        label=_('Subject'),
        widget=forms.TextInput(attrs={'size': settings.SINGLELINELEN}),
        required=False)

    message_text = forms.CharField(
        label=_('Message Text'),
        widget=forms.Textarea(attrs={'rows': settings.TEXTAREAROWS,
                                     'cols': settings.TEXTAREACOLS}),
        required=False)

    attachment = MultiFileField(
        label=_('Attachment'),
        required=False,
        count=1)

    saved_files = MultyChecksum(required=False, widget=forms.HiddenInput())

MESSAGE_ACTIONS = ((0, _('Choose one action')),
                   (1, _('Mark read')),
                   (2, _('Mark unread')),
                   (3, _('Delete')),
                   (4, _('Undelete')), )


class MessageActionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        message_list = kwargs.pop('message_list')
        server = kwargs.pop('server')
        super(MessageActionForm, self).__init__(*args, **kwargs)

        # Populate the identity choices
        self.fields['messages'].choices = message_list

        # And the folder list
        server.folder_iterator = 'iter_all'
        server.refresh_folders()
        self.fields['folder'].choices = [(folder.url(), "%s%s" % (
           '__' * folder.level(), folder.unicode_name())) for folder in server]

    messages = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    action = forms.ChoiceField(choices=MESSAGE_ACTIONS)
    folder = forms.ChoiceField()
