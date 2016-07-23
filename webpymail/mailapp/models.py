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

'''Model file for the mailapp'''

# Global imports:
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Models:

class UserIdentity(models.Model):
    profile = models.ForeignKey('UserProfile')

    name  = models.CharField(
        verbose_name=_('User name'),
        max_length=128,
        blank=True)

    mail_address = models.EmailField(
        verbose_name=_('Mail address'),
        max_length=128)

    signature = models.TextField(
        max_length=1024,
        verbose_name=_('Signature'),
        blank=True)

    use_signature = models.BooleanField(
        verbose_name=_('Use signature'),
        default=True)

    use_doubledash = models.BooleanField(
        verbose_name=_('Use double dash'),
        default=True)

    time_zone = models.CharField(
        verbose_name=_('Time zone'),
        max_length=64, default='GMT')

    citation_start = models.TextField(
        max_length=256,
        verbose_name=_('Citation start'),
        blank = True)

    citation_end = models.TextField(
        max_length=256,
        verbose_name=_('Citation end'),
        blank = True)

    def __unicode__(self):
        if self.name:
            return '"%s" <%s>' % (self.name, self.mail_address)
        else:
            return '<%s>' % (self.mail_address)
    class Admin:
        pass

    class Meta:
        verbose_name = _('Identity')
        verbose_name_plural = _('Identities')

class UserProfile(models.Model):
    '''User configuration options.

    This record is automatically created on the user first login on the system.
    '''
    user = models.OneToOneField(User)
    default_identity = models.OneToOneField(UserIdentity, null=True)
    sent_folder = models.TextField(max_length=128, default='INBOX')

    def __unicode__(self):
        return self.user.__unicode__()

    class Admin:
        list_display = ('user', )

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

class FoldersToExpand(models.Model):
    '''List of folders to expand. This table is managed from
    folder_views.py
    '''
    user = models.ForeignKey(User)
    folder_name = models.TextField(max_length=512)

class Attachments(models.Model):
    user     = models.ForeignKey(User)
    temp_file = models.TextField(max_length=128)
    filename = models.TextField(max_length=128)
    mime_type = models.TextField(max_length=128)
    content_id = models.TextField(max_length=128, blank = True)
    content_desc = models.TextField(max_length=128, blank = True)
    show_inline = models.BooleanField(default=False)
    size = models.IntegerField(default=0)
    sent = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)

    def media(self):
        try:
            return self.mime_type.split('/')[0].upper()
        except:
            return 'APPLICATION'

    def media_subtype(self):
        try:
            return self.mime_type.split('/')[1].upper()
        except:
            return 'OCTET-STREAM'

    def delete_button(self):
        return '<input type="submit" name="delete_%s" value="%s">' % (
            self.id, _('Remove'))
