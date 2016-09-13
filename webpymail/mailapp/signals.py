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

# Global imports
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Local imports
from mailapp.models import UserProfile, UserIdentity


def create_user_profile(sender, instance, created, **kwargs):
    '''
    Autocreate the user profile on new user creation
    '''
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)


def create_user_identity(sender, instance, created, **kwargs):
    '''
    On new user profile save, create a default identity
    '''
    if created:
        identity = UserIdentity(
                profile=instance,
                mail_address=instance.user.username)
        identity.save()
        instance.default_identity = identity
        instance.save()
post_save.connect(create_user_identity, sender=UserProfile)
