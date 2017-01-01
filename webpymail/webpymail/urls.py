
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

"""Base URL definitions
"""

# Global imports:
from django.conf import settings
from django.conf.urls import include, url

# Local Imports
from mailapp.views.message import index, not_implemented
from webpymail.views import about

urlpatterns = [
        # Root:
        url(r'^$', index),
        # About:
        url(r'^about/', about, name='about'),
        # Mail Interface:
        url(r'^mail/', include('mailapp.urls')),
        # Address book:
        url(r'^ab/', include('sabapp.urls')),
        # Authentication interface:
        url(r'^auth/', include('wpmauth.urls')),
        # Configuration:
        url(r'^config/', include('configapp.urls')),
        # Generic:
        url(r'^not_implemented/$', not_implemented, name='not_implemented'),
        ]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
