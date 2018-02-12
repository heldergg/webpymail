# -*- coding: utf-8 -*-

# imaplib2 python module, meant to be a replacement to the python default
# imaplib module
# Copyright (C) 2008 Helder Guerreiro

# This file is part of imaplib2.
#
# imaplib2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# imaplib2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

'''Replacement for the standard python module imaplib.

However this is not a drop in replacement and there's no easy path to migrate
programs based on 'imaplib' to this library.

The package contents are:

* imapll - low level imap library, it makes no attempt to parse the server
responses;
* imapp - parsed imap library;
* parsefetch - parses the fetch command responses;
* parselist - parses the list and lsub commands responses;
* sexp - scans nested parentheses lists on a string and transforms it in python
lists;
* infolog - example infolog class;
* utils - severall utility functions and classes;
'''

D_SERVER = 1        # Debug responses from the server
D_CLIENT = 2        # Debug data sent by the client
D_RESPONSE = 4      # Debug obtained response
