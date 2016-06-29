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

import os.path

# Django settings for webpymail project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('SysAdm', 'sysadm@example.com'),
)
MANAGERS = ADMINS

# Local time zone for this installation.
# Choices can be found here:
#  http://www.postgresql.org/docs/8.1/static/datetime-keywords.html
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as
# your system time zone.
TIME_ZONE = 'WET'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = './media/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8v7=r99a*pjt(c@es=7wc1q2#d8ycj1!j6*zoy@pdg2y8@b*wt'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'themesapp.context_processors.theme_name')

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
)

ROOT_URLCONF = 'webpymail.urls'

PROJDIR = os.path.join( os.path.abspath(os.path.dirname(__file__)), '..' )
TEMPLATE_DIRS = ( os.path.join(PROJDIR, 'templates').replace('\\', '/'), )

INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',

    # WebPyMail apps
    'wpmauth',
    'mailapp',
    'sabapp',
    'themesapp',
)

######################
# WEBPYMAIL SETTINGS #
######################

DEFAULT_FOLDER = 'INBOX'

###################
# DJANGO SETTINGS #
###################

# Database Setup:

DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3',
                           'NAME': './webpymail.db',
                         }
            }

# User profiles:

AUTH_PROFILE_MODULE = 'mailapp.UserProfile'

# SESSIONS

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 28800       # 8 hours
SESSION_COOKIE_SECURE = False    # set to True if using https
SESSION_COOKIE_NAME = 'wpm_sessionid'

# AUTHENTICATION

AUTHENTICATION_BACKENDS = (
    'wpmauth.backends.ImapBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

LOGIN_URL  = '/auth/login/'
LOGOUT_URL = '/auth/logout/'

# DISPLAY SETTINGS

# TODO: this should be an user setting:
MESSAGES_PAGE = 50 # Number of messages per page to display

# Mail compose form
MAXADDRESSES = 50   # Maximum number of mails that can be used on a To, Cc or
                    # Bcc field.
SINGLELINELEN = 60
TEXTAREAROWS = 15
TEXTAREACOLS = 60

# Attachments

TEMPDIR = '/tmp' # Temporary dir to store the attachements

# User configuration dir:
BASEDIR = os.path.abspath(os.path.dirname(__file__))

CONFIGDIR = os.path.join('/home/helder/prg/webpymail-config')
USERCONFDIR = os.path.join(CONFIGDIR, 'users')
SERVERCONFDIR = os.path.join(CONFIGDIR, 'servers')
FACTORYCONF = os.path.join(CONFIGDIR,'factory.conf')
DEFAULTCONF = os.path.join(CONFIGDIR,'defaults.conf')
SERVERCONF  = os.path.join(CONFIGDIR,'servers.conf')
SYSTEMCONF  = os.path.join(CONFIGDIR,'system.conf')

###############################################
# Do not change anything beyond this point... #
###############################################

WEBPYMAIL_VERSION = 'SVN'

##
## LOCAL SETTINGS
##

try:
    from local_settings import *
except ImportError:
    pass
