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

from django import template
from django.template import resolve_variable
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape

register = template.Library()

import re, textwrap

# TODO: This regex needs some tweeking to the query part:
html_url_re = re.compile(r"(https?://(?:(?:(?:(?:(?:[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z0-9])\.)*(?:[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]))|(?:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+))(?::[0-9]+)?)(?:/(?:(?:(?:[a-zA-Z]|[0-9]|[$\-_.+]|[!*'(),])|(?:%[0-9A-Fa-f][0-9A-Fa-f]))|[;:@&=])*(?:/(?:(?:(?:[a-zA-Z]|[0-9]|[$\-_.+]|[!*'(),])|(?:%[0-9A-Fa-f][0-9A-Fa-f]))|[;:@&=])*)*(?:\?(?:(?:(?:[a-zA-Z]|[0-9]|[$\-_.+]|[!*'(),])|(?:%[0-9A-Fa-f][0-9A-Fa-f]))|[;:@&=])*)?)?)")

# Tag to retrieve a message part from the server:

@register.tag(name="show_part")
def do_show_part(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, message, part = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires two args: message, part" \
            % token.contents.split()[0])

    return PartTextNode(message, part)

def make_links( match ):
    url = match.groups()[0]
    return '<a href="%s">\n%s</a>' % (url, url)

def wrap_lines(text, colnum = 72):
    ln_list = text.split('\n')
    new_list = []
    for ln in ln_list:
        if len(ln) > colnum:
            ln = textwrap.fill(ln, colnum)
        new_list.append(ln)

    return '\n'.join(new_list)

class PartTextNode(template.Node):
    def __init__(self, message, part ):
        self.message = message
        self.part = part

    def render(self, context):
        message =  resolve_variable(self.message, context)
        part = resolve_variable(self.part, context)
        text = escape(message.part( part ))
        text = html_url_re.sub( make_links, text)
        if part.media == 'TEXT' and part.media_subtype == 'PLAIN':
            text = wrap_lines( text, 80 )
        return text
