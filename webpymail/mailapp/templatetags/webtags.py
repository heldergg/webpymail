# -*- coding: utf-8 -*-

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

from django import template
from django.template import TemplateSyntaxError
from django.template.base import Variable

register = template.Library()

# Tag to retrieve a message part from the server:


@register.tag(name="spaces")
def do_spaces(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, num_spaces = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError('%r tag requires one arg: num_spaces'
                                  % token.contents.split()[0])
    return PartTextNode(num_spaces)


class PartTextNode(template.Node):
    def __init__(self, num_spaces):
        self.num_spaces = num_spaces

    def render(self, context):
        num_spaces = Variable(self.num_spaces).resolve(context)
        try:
            num_spaces = int(num_spaces)
        except ValueError:
            raise TemplateSyntaxError('do_spaces tag\'s num_spaces argument '
                                      'must be an int')
        return '&nbsp;&nbsp;' * num_spaces

# Given a variable of type QueryDict it will update it and display the
# resulting query


@register.tag(name="queryupdate")
def do_queryupdate(parser, token):
    try:
        tokens = token.split_contents()
        if len(tokens) == 2:
            tag_name, query = tokens
            query_parts = []
        else:
            tag_name, query, *query_parts = tokens
    except ValueError:
        raise TemplateSyntaxError('%r tag requires ot least two args. The '
                                  'first must be a variable of type QueryDict,'
                                  ' and then one or assignement expressions. '
                                  'The first must be a variable of type '
                                  'QueryDict and then one or query variables '
                                  'to create or update.')
    return UpdateQueryNode(query, query_parts)


class UpdateQueryNode(template.Node):
    def __init__(self, query, parts):
        self.query = Variable(query)
        self.parts = self.query_update(parts)

    def query_update(self, query_parts):
        parts = []
        for part in query_parts:
            parts.append(part.split('='))
        return parts

    def render(self, context):
        query = self.query.resolve(context).copy()
        for var, value in self.parts:
            if (value[0] == value[-1] and value[0] in ('\'', '"') and
                    len(value[0]) > 2):
                query[var] = value[1:-1]
            else:
                query[var] = Variable(value).resolve(context)
        query_str = query.urlencode()
        if query_str:
            return '?%s' % query_str
        else:
            return ''
