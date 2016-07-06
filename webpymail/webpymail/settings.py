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

'''
Django default settings for webpymail
'''

DEBUG=True

##
## BASE PATHS
##

import os.path
PROJECT_DIR = os.path.abspath(os.path.join( os.path.dirname( __file__ ), '../..'))
DJANGO_DIR = os.path.abspath(os.path.join( os.path.dirname( __file__ ), '..'))

##
## Site admins and security
##

ADMINS = (
    ('SysAdm', 'sysadm@example.com'),
)
MANAGERS = ADMINS

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8v7=r99a*pjt(c@es=7wc1q2#d8ycj1!j6*zoy@pdg2y8@b*wt'

##
## Time and Language
##

# Local time zone for this installation.
# Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as
# your system time zone.
TIME_ZONE = 'WET'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# A boolean that specifies if localized formatting of data will be
# enabled by default or not. If this is set to True, e.g. Django will
# display numbers and dates using the format of the current locale.
USE_L10N = True

##
## Static files
##

# media  = user generated content
# static = site's static files

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join( PROJECT_DIR, 'collected_static' )

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(DJANGO_DIR, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

##
## Templates
##

TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [ os.path.join(PROJECT_DIR, 'templates'), ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                    'django.core.context_processors.request',
                    'themesapp.context_processors.theme_name'
                    ],
                }
            }
        ]


##
## Applications and middleware
##

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
)

ROOT_URLCONF = 'webpymail.urls'

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

##
## DATABASE
##

# Database Setup:
DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3',
                           'NAME': './webpymail.db',
                         }
            }

##
## Autentication and sessions
##

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

##
## Webpymail specific settings
##

DEFAULT_FOLDER = 'INBOX'

# DISPLAY SETTINGS

# TODO: this should be an user setting:
MESSAGES_PAGE = 50 # Number of messages per page to display

# Mail compose form
MAXADDRESSES = 50   # Maximum number of addresses that can be used on a To, Cc
                    # or Bcc field.
SINGLELINELEN = 60
TEXTAREAROWS = 15
TEXTAREACOLS = 60

# Attachments

TEMPDIR = '/tmp' # Temporary dir to store the attachements

# User configuration directories:
CONFIGDIR = PROJECT_DIR
USERCONFDIR = os.path.join(CONFIGDIR, 'users')
SERVERCONFDIR = os.path.join(CONFIGDIR, 'servers')
FACTORYCONF = os.path.join(CONFIGDIR,'factory.conf')
DEFAULTCONF = os.path.join(CONFIGDIR,'defaults.conf')
SERVERCONF  = os.path.join(CONFIGDIR,'servers.conf')
SYSTEMCONF  = os.path.join(CONFIGDIR,'system.conf')

###############################################
# Do not change anything beyond this point... #
###############################################

WEBPYMAIL_VERSION = 'GIT'

##
## LOCAL SETTINGS
##

try:
    from local_settings import *
except ImportError:
    pass
