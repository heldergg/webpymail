# -*- coding: utf-8 -*-

# themesapp - Simple Address Book Application
# Copyright (C) 2008 Helder Guerreiro

# This file is part of themesapp.
#
# themesapp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# themesapp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with themesapp.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

from django.conf import settings
from django.shortcuts import render as django_render

from utils.config import WebpymailConfig

DEFAULT_THEME = getattr(settings, 'DEFAULT_THEME', 'default')


def get_theme(request):
    '''
    Returns the current theme.

    The theme name can be defined in this order (the first found is used):

        1. GET request query theme=<theme name>
        2. Django session key 'theme'
        3. If the user is authenticated, the configuration key general.theme
           is read
        4. The default theme defined in the django settings file with the key
           DEFAULT_THEME
    '''
    # From the GET request
    theme = request.GET.get('theme', None)
    if theme:
        request.session['theme'] = theme
        return theme

    # From the django session
    theme = request.session.get('theme', None)
    if theme:
        return theme

    # From Webpymail configuration
    config = WebpymailConfig(request)
    theme = config.get('general', 'theme')
    if theme:
        request.session['theme'] = theme
        return theme

    # From settings.py
    return DEFAULT_THEME


def render(request, template_name, context=None, content_type=None,
           status=None, using=None):
    '''
    This is a version of the default django render shortcut.

    No deprecated args as of django 1.9 are used.

    Just like the original it returns a HttpResponse whose content is
    filled with the result of calling django.template.loader.render_to_string()
    with the passed arguments.

    Besides this, if the template argument is a string then transforms it into
    a template list in the form:

    [<theme name>/<template name>,
     <default theme>/<template name>,
     <template name>]

    The first template to be found is used.
    '''
    theme = get_theme(request)
    if settings.DEBUG:
        print('get_theme returns:', theme)
    template = [
            '%s/%s' % (theme, template_name),
            '%s/%s' % (DEFAULT_THEME, template_name),
            template_name]
    return django_render(request, template, context=context,
                         content_type=content_type, status=status, using=using)
