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

from django import template
from django.template import resolve_variable
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape

register = template.Library()

import re, textwrap

# TODO: This regex needs some tweeking to the query part:
html_url_re = re.compile(r"(https?://(?:(?:(?:(?:(?:[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z0-9])\.)*(?:[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]|[a-zA-Z]))|(?:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+))(?::[0-9]+)?)(?:/(?:(?:(?:[a-zA-Z]|[0-9]|[$\-_.+]|[!*'(),])|(?:%[0-9A-Fa-f][0-9A-Fa-f]))|[;:@&=])*(?:/(?:(?:(?:[a-zA-Z]|[0-9]|[$\-_.+]|[!*'(),])|(?:%[0-9A-Fa-f][0-9A-Fa-f]))|[;:@&=])*)*(?:\?(?:(?:(?:[a-zA-Z]|[0-9]|[$\-_.+]|[!*'(),])|(?:%[0-9A-Fa-f][0-9A-Fa-f]))|[;:@&=])*)?)?)")

# Tag to retrieve a message part from the server:

@register.tag(name="part_text")
def do_part_text(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, message, part, media_subtype = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires three args: message, part, media_subtype" \
            % token.contents.split()[0]
    if not (media_subtype[0] == media_subtype[-1] and media_subtype[0] in ('"', "'")):
        raise template.TemplateSyntaxError, \
            "%r tag's media_subtype argument should be in quotes" % tag_name

    return PartTextNode(message, part, media_subtype[1:-1])

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
    def __init__(self, message, part, media_subtype):
        self.media_subtype = media_subtype.upper()
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
