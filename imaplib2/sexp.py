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

# Global imports
import re

# Regexp
literal_re = re.compile(r'^{(\d+)}\r\n')
simple_re = re.compile(r'^([^ ()\[]+(?:\[[^\]]*\])?)')
quoted_re = re.compile(r'^"((?:[^"\\]|\\")*?)"')

# Errors


class SError(Exception):
    pass


def scan_sexp(text):
    '''S-Expression scanner.

    This is a non-recursive version. It uses the lists property of assigning
    only by reference to assemble the s-exp.

    @param text: text to be scanned.
    @type  text: s-exp string


    @return result: s-exp in a python list.
    '''

    # Initialization
    pos = 0
    lenght = len(text)
    result = []
    cur_result = result
    level = [cur_result]

    # Scanner
    while pos < lenght:

        # Quoted literal:
        if text[pos] == '"':
            quoted = quoted_re.match(text[pos:])
            if quoted:
                cur_result.append(quoted.groups()[0])
                pos += quoted.end() - 1

        # Numbered literal:
        elif text[pos] == '{':
            lit = literal_re.match(text[pos:])
            if lit:
                start = pos+lit.end()
                end = pos+lit.end()+int(lit.groups()[0])
                pos = end - 1
                cur_result.append(text[start:end])

        # Simple literal
        elif text[pos] not in '() ':
            simple = simple_re.match(text[pos:])
            if simple:
                tmp = simple.groups()[0]
                if tmp == 'NIL':
                    tmp = None
                cur_result.append(tmp)
                pos += simple.end() - 1

        # Level handling, if we find a '(' we must add another list, if we
        # find a ')' we must return to the previous list.
        elif text[pos] == '(':
            cur_result.append([])
            cur_result = cur_result[-1]
            level.append(cur_result)

        elif text[pos] == ')':
            try:
                cur_result = level[-2]
                del level[-1]
            except IndexError:
                raise SError('Unexpected parenthesis at pos %d' % pos)

        pos += 1

    return result

if __name__ == '__main__':
    from time import time

    count = 1000
    text = '(A NIL {5}\r\n12345 (D E))(F G)'
    text = ('266 FETCH (FLAGS (\Seen) UID 31608 INTERNALDATE '
            '"30-Jan-2008 02:48:01 +0000" RFC822.SIZE 4509 ENVELOPE '
            '("Tue, 29 Jan 2008 14:00:24 +0000" "Aprenda as tXcnicas e os '
            'truques da cozinha mais doce..." (("Ediclube" NIL "ediclube" '
            '"sigmathis.info")) (("Ediclube" NIL "ediclube" "sigmathis.info"))'
            ' ((NIL NIL "ediclube" "sigmathis.info")) ((NIL NIL "helder" '
            '"example.com")) NIL NIL NIL "<64360f85d83238281a27b921fd3e7eb3@'
            'localhost.localdomain>"))')
    # text = 'A B (C NIL (D E))(F G)'

    itx = 300
    rit = range(itx)

    print('Test to the s-exp parser:')
    print()

    print('Non Recursive (%d times):' % itx)
    a = time()
    for i in rit:
        scan_sexp(text)
    b = time()
    print(1000 * (b-a) / itx, 'ms/iter')
    print(itx, ' --> ', 1000 * (b-a), 'ms')
    print()
    print(scan_sexp(text))
