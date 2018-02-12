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

'''Parse the fetch responses.
'''

# Imports
from .utils import (getUnicodeHeader, getUnicodeMailAddr,
                    internaldate2datetime, envelopedate2datetime)
from .sexp import scan_sexp

# Body structure


class BODYERROR(Exception):
    pass


class BodyPart:
    def __init__(self, structure, prefix, level, next_part, parent=None):
        self.parent = parent

    def query(self):
        raise BODYERROR('This part is not numbered')

    def load_parts(self, structure, prefix):
        raise BODYERROR('This part is not numbered')

    def fetch_query(self):
        '''Fetch query to retrieve this part'''
        raise BODYERROR('This part is not numbered')

    def represent(self):
        '''Returns a string that depicts the message structure. Only for
        informational pourposes.
        '''
        raise BODYERROR('Abstract method')

    # Methods to facilitate displaying the message:

    def serial_message(self):
        '''Returns the message structure as a one dimension list'''
        return [self]

    def find_part(self, part_number):
        '''Returns a part'''
        for part in self.serial_message():
            if part.part_number == part_number:
                return part
        raise BODYERROR('Didn\'t find the requested part (%s).' % part_number)

    def is_text(self):
        '''Only true for media='TEXT' media_subtype='PLAIN' or 'HTML' '''
        return False

    def is_basic(self):
        '''Only true for media!='TEXT' '''
        return False

    def is_multipart(self):
        '''Only true for media='MULTIPART'  '''
        return False

    def test_media(self, media):
        return self.media == media.upper()

    def test_subtype(self, media_subtype):
        return self.media_subtype == media_subtype.upper()

    def is_plain(self):
        return self.test_subtype('PLAIN')

    def is_html(self):
        return self.test_subtype('HTML')

    def is_encapsulated(self):
        '''Only valid for encapsulated messages'''
        return False

    def is_attachment(self):
        '''Only valid for single parts that are attachments'''
        return self.is_basic()


class Multipart(BodyPart):
    def __init__(self, structure, prefix, level, next_part, parent=None):
        BodyPart.__init__(self, structure, prefix, level, next_part, parent)
        if next_part:  # has part number
            self.part_number = '%s%d' % (prefix, level)
            prefix = '%s%d.' % (prefix, level)
        else:
            next_part = True
            self.part_number = None
        self.media = 'MULTIPART'
        self.part_list = []
        self.body_ext_mpart = []
        self.load_parts(structure, prefix, level, next_part)

    def load_parts(self, structure, prefix, level, next_part):
        is_subpart = True
        level = 1
        for part in structure:
            if is_subpart:
                if isinstance(part, list):
                    # We have one more subpart
                    self.part_list.append(load_structure(part, prefix, level,
                                                         next_part, self))
                    level += 1
                else:
                    # The subpart list ended, the present field is the media
                    # subtype
                    is_subpart = False
                    self.media_subtype = part
            else:
                # We have body_ext_mpart, for now we ignore this
                self.body_ext_mpart.append(part)

    def __str__(self):
        return '<MULTIPART/%s>' % self.media_subtype

    def represent(self):
        try:
            rpr = '%-10s %s/%s\n' % (self.part_number, self.media,
                                     self.media_subtype)
        except:
            rpr = '%-10s %s/%s\n' % (' ', self.media, self.media_subtype)

        for part in self.part_list:
            rpr += part.represent()

        return rpr

    def fetch_query(self, media, media_subtype):
        tmp_query = []
        for part in self.part_list:
            query = part.fetch_query(media, media_subtype)
            if query:
                tmp_query.append(query)

        return ' '.join(tmp_query)

    def serial_message(self):
        tmp_partlist = [self]
        for part in self.part_list:
            tmp_partlist += part.serial_message()
        return tmp_partlist

    def is_multipart(self):
        '''Only true for media='MULTIPART'  '''
        return True

    def is_alternative(self):
        return self.test_subtype('ALTERNATIVE')

    def len(self):
        '''Number of first level parts that constitute this part'''
        return len(self.part_list)

    def has_html(self):
        '''True is one of the first level subparts if of media type
        TEXT/HTML'''
        for part in self.part_list:
            if not part.is_multipart():
                if part.is_text() and part.is_html():
                    return True
            else:
                return part.has_html()
        return False


class Single (BodyPart):
    def __init__(self, structure, prefix, level, next_part, parent=None):
        BodyPart.__init__(self, structure, prefix, level, next_part, parent)
        self.media = structure[0].upper()
        self.media_subtype = structure[1].upper()
        self.body_fld_id = structure[3]
        self.body_fld_desc = structure[4]
        self.body_fld_enc = structure[5]
        self.body_fld_octets = structure[6]

        # body_fld_param = structure[2]
        # if body_fld_param is NIL, then there are no param
        self.body_fld_param = {}
        if structure[2]:
            it = iter(structure[2])
            for name, value in zip(it, it):
                if name:
                    self.body_fld_param[name.upper()] = value

        self.part_number = '%s%d' % (prefix, level)

    def charset(self):
        if 'CHARSET' in self.body_fld_param:
            return self.body_fld_param['CHARSET']
        else:
            return 'iso-8859-1'

    def filename(self):
        # TODO: first look for the name on the Content-Disposition header
        # and only after this one should look on the Constant-Type Name
        # parameter
        if 'NAME' in self.body_fld_param:
            return getUnicodeHeader(self.body_fld_param['NAME'])
        else:
            return None

    def represent(self):
        return '%-10s %s/%s\n' % (self.part_number, self.media,
                                  self.media_subtype)

    def is_attachment(self):
        return bool(self.filename())

    def is_last(self):
        '''True if part is a last part in a multipart message'''
        if not self.parent:
            raise BODYERROR('This part has no parent')
        return self.parent.part_list[-1] == self

    def __str__(self):
        return '<%s/%s>' % (self.media, self.media_subtype)


class Message(Single):
    def __init__(self, structure, prefix, level, next_part, parent=None):
        Single.__init__(self, structure, prefix, level, next_part, parent)

        prefix = '%s%d.' % (prefix, level)
        if isinstance(structure[8], list):
            # Embeded message is a multipart
            next_part = False

        # Rest
        self.envelope = Envelope(structure[7])
        self.body = load_structure(structure[8], prefix, 1, next_part, self)
        self.body_fld_lines = structure[9]

        if len(structure) > 10:
            self.body_ext_1part = structure[10:]

        self.start = True

    def represent(self):
        rpr = Single.represent(self)
        rpr += self.body.represent()
        return rpr

    def fetch_query(self, media, media_subtype):
        return self.body.fetch_query(media, media_subtype)

    def serial_message(self):
        return [self] + self.body.serial_message() + [self]

    def is_encapsulated(self):
        return True

    def is_start(self):
        tmp = self.start
        self.start = not self.start
        return tmp


class SingleTextBasic (Single):
    def __init__(self, structure, prefix, level, next_part, parent=None):
        Single.__init__(self, structure, prefix, level, next_part, parent)

    def __str__(self):
        return '<%s/%s>' % (self.media, self.media_subtype)

    def query(self):
        return 'BODY[%s]' % self.part_number

    def fetch_query(self, media, media_subtype):
        if (self.media == media and self.media_subtype == media_subtype) or \
           (self.media == media and media_subtype == '*') or \
           (media == '*' and self.media_subtype == media_subtype) or \
           (media == '*' and media_subtype == '*'):
            return self.query()
        else:
            return None

    def process_body_ext_1part(self):
        self.body_fld_md5 = None
        self.body_fld_dsp = None
        self.body_fld_lang = None
        self.body_fld_loc = None
        self.body_extension = None

        if isinstance(self.body_ext_1part, list):
            self.body_fld_md5 = self.body_ext_1part[0]

            if len(self.body_ext_1part) > 1:
                self.body_fld_dsp = self.body_ext_1part[1]
            if len(self.body_ext_1part) > 2:
                self.body_fld_lang = self.body_ext_1part[2]
            if len(self.body_ext_1part) > 3:
                self.body_fld_loc = self.body_ext_1part[3]
            if len(self.body_ext_1part) > 4:
                self.body_extension = self.body_ext_1part[4:]
        else:
            self.body_fld_md5 = self.body_ext_1part

    def is_attachment(self):
        if self.body_fld_dsp:
            return self.body_fld_dsp[0].upper() == 'ATTACHMENT'
        else:
            return Single.is_attachment(self)


class SingleText (SingleTextBasic):
    def __init__(self, structure, prefix, level, next_part, parent=None):
        SingleTextBasic.__init__(self, structure, prefix,
                                 level, next_part, parent)
        self.body_fld_lines = structure[7]

        self.body_ext_1part = None
        if len(structure) > 8:
            self.body_ext_1part = structure[8:]
        self.process_body_ext_1part()

    def is_text(self):
        return True


class SingleBasic (SingleTextBasic):
    def __init__(self, structure, prefix, level, next_part, parent=None):
        SingleTextBasic.__init__(self, structure, prefix,
                                 level, next_part, parent)

        self.body_ext_1part = None
        if len(structure) > 7:
            self.body_ext_1part = structure[7:]
        self.process_body_ext_1part()

    def is_basic(self):
        '''Only true for media!='TEXT' '''
        return True


def load_structure(structure, prefix='',
                   level=1, next_part=False, parent=None):
    if isinstance(structure[0], list):
        # It's a multipart
        return Multipart(structure, prefix, level, next_part, parent)

    media = structure[0].upper()
    media_subtype = structure[1].upper()

    if media == 'MESSAGE' and media_subtype == 'RFC822':
        return Message(structure, prefix, level, next_part, parent)

    if media == 'TEXT':
        return SingleText(structure, prefix, level, next_part, parent)

    return SingleBasic(structure, prefix, level, next_part, parent)


def envelope(structure):
    return {'env_date': envelopedate2datetime(structure[0]),
            'env_subject': getUnicodeHeader(structure[1]),
            'env_from': getUnicodeMailAddr(structure[2]),
            'env_sender': getUnicodeMailAddr(structure[3]),
            'env_reply_to': getUnicodeMailAddr(structure[4]),
            'env_to': getUnicodeMailAddr(structure[5]),
            'env_cc': getUnicodeMailAddr(structure[6]),
            'env_bcc': getUnicodeMailAddr(structure[7]),
            'env_in_reply_to': structure[8],
            'env_message_id': structure[9]}


def real_name(address):
    '''From an address returns the person real name or if this is empty the
    email address'''
    if address[0]:
        return address[0]
    else:
        return address[1]


class Envelope(dict):
    def __init__(self, env):
        dict.__init__(self, envelope(env))

    def short_mail_list(self, mail_list):
        for addr in mail_list:
            yield real_name(addr)

    def to_short(self):
        '''Returns a list with the first and last names'''
        return self.short_mail_list(self['env_to'])

    def from_short(self):
        '''Returns a list with the first and last names'''
        return self.short_mail_list(self['env_from'])

    def cc_short(self):
        '''Returns a list with the first and last names'''
        return self.short_mail_list(self['env_cc'])


class FetchParser(dict):
    '''This class parses the fetch response (already as a python dict) and
    further processes.
    '''

    def __init__(self, result):
        # Scan the message and make it a dict
        it = iter(scan_sexp(result)[0])
        result = dict(list(zip(it, it)))

        dict.__init__(self, result)

        for data_item in self:
            method_name = data_item + '_data_item'
            meth = getattr(self, method_name, self.default_data_item)
            self[data_item] = meth(self[data_item])

    def default_data_item(self, data_item):
        return data_item

    def UID_data_item(self, uid):
        return int(uid)

    def BODY_data_item(self, body):
        return load_structure(body)

    BODYSTRUCTURE_data_item = BODY_data_item

    def INTERNALDATE_data_item(self, arrival):
        return internaldate2datetime(arrival)

    def ENVELOPE_data_item(self, envelope):
        return Envelope(envelope)
