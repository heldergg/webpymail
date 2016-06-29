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

register = template.Library()

# Tag to retrieve a message part from the server:

@register.tag(name="spaces")
def do_spaces(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, num_spaces = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires one arg: num_spaces" \
            % token.contents.split()[0]

    return PartTextNode(num_spaces)

class PartTextNode(template.Node):
    def __init__(self, num_spaces):
        self.num_spaces = num_spaces

    def render(self, context):
        num_spaces =  resolve_variable(self.num_spaces, context)
        try:
            num_spaces = int(num_spaces)
        except ValueError:
            raise template.TemplateSyntaxError, \
                "%r tag's num_spaces argument must be an int" % tag_name

        return '&nbsp;&nbsp;' * num_spaces
