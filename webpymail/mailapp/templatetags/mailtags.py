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

import bleach
import re, textwrap

# Bleach configuration
TAGS = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code',
        'em', 'em', 'h1', 'h2', 'h3', 'h4' 'hr', 'i', 'li', 'ol', 'p',
        'strong', 'style', 'ul', 'div', 'table', 'th', 'td', 'tr',
        'div', 'span', 'img']
STYLES = ['azimuth', 'background-color', 'border-bottom-color',
          'border-collapse', 'border-color', 'border-left-color',
          'border-right-color', 'border-top-color', 'clear',
          'color', 'cursor', 'direction', 'display', 'elevation',
          'float', 'font', 'font-family', 'font-size', 'font-style',
          'font-variant', 'font-weight', 'height', 'letter-spacing',
          'line-height', 'overflow', 'pause', 'pause-after',
          'pause-before', 'pitch', 'pitch-range', 'richness',
          'speak', 'speak-header', 'speak-numeral', 'speak-punctuation',
          'speech-rate', 'stress', 'text-align', 'text-decoration',
          'text-indent', 'unicode-bidi', 'vertical-align',
          'voice-family', 'volume', 'white-space', 'width']
ATTRS = {'*': ['class', 'id', 'style', ],
         'a': ['href', 'title'],
         'abbr': ['title'],
         'acronym': ['title'],
         'img': ['alt','title', 'width', 'height'],
         'table': ['width', 'align', 'cellpadding', 'cellspacing',
                   'border'],
         'td': ['width', 'valign'],
         'th': ['width', 'valign'],
         }
PROTOCOLS = ['http', 'https', 'mailto'] # Not available in bleach 1.4.3

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

def wrap_lines(text, colnum = 72):
    ln_list = text.split('\n')
    new_list = []
    for ln in ln_list:
        if len(ln) > colnum:
            ln = textwrap.fill(ln, colnum)
        new_list.append(ln)
    return '\n'.join(new_list)

class PartTextNode(template.Node):
    def __init__(self, message, part, external_images=True ):
        self.message = message
        self.part = part
        self.external_images = external_images

    def sanitize_text(self, text):
        text = escape(text)
        # text = html_url_re.sub(make_links, text)
        text = bleach.linkify(text)
        text = wrap_lines( text, 80 )
        return text

    def sanitize_html(self, text):
        if self.external_images:
            ATTRS['img'].append('src')
        text = bleach.clean(text,
                tags=TAGS,
                attributes=ATTRS,
                styles=STYLES,
                strip=True)
        return text

    def render(self, context):
        message =  resolve_variable(self.message, context)
        part = resolve_variable(self.part, context)
        text = message.part(part)
        if part.is_plain():
            text = self.sanitize_text(text)
        elif part.is_html():
            text = self.sanitize_html(text)
        return text
