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
from django.core.urlresolvers import reverse

register = template.Library()

import bleach
import re, textwrap

##
## HTML sanitization
##

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
         'img': ['src','alt','title', 'width', 'height'],
         'table': ['width', 'align', 'cellpadding', 'cellspacing',
                   'border'],
         'td': ['width', 'valign'],
         'th': ['width', 'valign'],
         }
PROTOCOLS = ['http', 'https', 'mailto'] # Not available in bleach 1.4.3


class HtmlSanitize:
    def __init__(self, message, part, external_images):
        self.message = message
        self.part = part
        self.external_images = external_images
        #self.external_images = False

    def get_html(self):
        return self.message.part(self.part)

    def bleach_html(self, html):
        print(html)
        html = bleach.clean(html,
                tags=TAGS,
                attributes=ATTRS,
                styles=STYLES,
                strip=True)
        return html.strip()

    def embedded_images(self, html):
        def process_src(src_match):
            src = src_match.group(0)
            src = src[5:-1]
            if src.startswith('cid:'):
                # Embedded image
                cid = src[4:]
                cid = cid.replace('<','').replace('>','')
                part = self.message.search_fld_id(cid)
                if part:
                    src = reverse(
                            'mailapp_mpart_inline',
                            kwargs={
                                'folder': self.message.folder.url(),
                                'uid': self.message.uid,
                                'part_number': part.part_number,
                                })
            elif not self.external_images:
                src = '/static/img/pixel.png'
            return 'src="%s"' % src
        html = re.sub(r'src=".+?"',process_src,html)
        return html

    def run(self):
        html = self.get_html()
        html = self.bleach_html(html)
        html = self.embedded_images(html)
        return html


##
## Tags
##

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

    def sanitize_html(self, message, part):
        return HtmlSanitize(message, part, self.external_images).run()

    def render(self, context):
        message =  resolve_variable(self.message, context)
        part = resolve_variable(self.part, context)
        if part.is_plain():
            text = self.sanitize_text(message.part(part))
        elif part.is_html():
            text = self.sanitize_html(message, part)
        return text
