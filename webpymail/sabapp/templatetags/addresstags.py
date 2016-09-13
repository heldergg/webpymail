# -*- coding: utf-8 -*-

# sabapp - Simple Address Book Application
# Copyright (C) 2008 Helder Guerreiro

# This file is part of sabapp.
#
# sabapp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# sabapp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sabapp.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

from django import template
from django.template import Node, NodeList
from django.template import Variable
from django.template.defaultfilters import stringfilter

from sabapp.models import Address

register = template.Library()


@register.tag(name="ifhasaddr")
def do_has_addr(parser, token):
    try:
        addr = token.split_contents()[1]
    except ValueError:
        raise template.TemplateSyntaxError(
            'ifhasaddr tag requires one argument: a tupple ("name", "email" )')

    nodelist_true = parser.parse(('else', 'endifhasaddr'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifhasaddr',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfHasAddrNode(addr, nodelist_true, nodelist_false)


class IfHasAddrNode(Node):
    child_nodelists = ('nodelist_true', 'nodelist_false')

    def __init__(self, addr, nodelist_true, nodelist_false=None):
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.addr = addr

    def __repr__(self):
        return "<IfHasAddr node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def render(self, context):
        request = Variable('request').resolve(context)
        addr = Variable(self.addr).resolve(context)

        if Address.objects.have_addr(request, addr[1]):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

#
# Filters
#


@stringfilter
def first_name(st):
    bits = st.split()
    if len(bits) > 1:
        return ' '.join(bits[:-1])
    else:
        return st.strip()

register.filter('first_name', first_name)


@stringfilter
def last_name(st):
    bits = st.split()
    if len(bits) > 1:
        return bits[-1]
    else:
        return ''

register.filter('last_name', last_name)
