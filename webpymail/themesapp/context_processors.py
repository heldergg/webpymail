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

from .shortcuts import get_theme


def theme_name(request):
    return {'theme': get_theme(request)}
