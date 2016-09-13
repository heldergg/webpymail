# -*- coding: utf-8 -*-

# hlimap - High level IMAP library
# Copyright (C) 2008 Helder Guerreiro

# This file is part of hlimap.
#
# hlimap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hlimap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hlimap.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

from .imapserver import ImapServer

'''High Level IMAP Lib

Introduction
============

This is a high level, object oriented library to handle IMAP connections from
python programs. It aims to hide the awkwardness of the imaplib shipped with
python.

This library only exports the L{ImapServer<ImapServer>} class.

ImapServer Class
================

class hlimap.ImapServer( host='localhost', port=None, ssl=False, keyfile=None,
                         certfile=None )

This class establishes the connection to the IMAP server. When instantiated the
resulting object can be used to access the folder tree and the messages.

Methods:

ImapServer.login(username, password) - Authenticates against the server.

ImapServer.set_special_folders(*folder_list) - stores the special folders, this
            information is used by the sort method. The special folders appear
            first on the folder list.

ImapServer.set_expand_list(*folder_list) - stores the folders to expand. Just
            as with the special folders, this is used when iterating through
            the folders. Only the folders set to expand will have their sub
            folders displayed.

ImapServer.refresh_folders(subscribed = True) - Extracts the folder list from
            the server. Retrieving the folder list is a lazy operation. If we
            want to access a single folder, we simply select it, so it's not
            necessary to retrieve the complete list.

ImapServer.set_folder_iterator() -  Sets the iterator to use when going through
            the folders. There are available several iterators defined on the
            FolderTree class.
            TODO: This iterator selection mechanism should be remade. This
            method is used only internally to the ImapServer class, however
            it's useful to change the iterator on the fly (that was the
            original objective), the current method is awkward.

ImapServer.__del__() - logs out of the imap server when the ImapServer instance
            is deleted.

ImapServer.__getitem__(path) - get a Folder object.

ImapServer.__iter__() - Iterates through the user accessible folders.


--------------------------------------------------------------------------------

FolderTree Class
================


Folder Class
============


Flags Class
===========


--------------------------------------------------------------------------------

MessageList Class
=================


Message Class
=============


Paginator Class
===============


Sorter Class
============


--------------------------------------------------------------------------------

Example Usage
=============

Server Level
------------

First we have to create an instance of L{ImapServer<ImapServer>}, and login
only the server:

'''
