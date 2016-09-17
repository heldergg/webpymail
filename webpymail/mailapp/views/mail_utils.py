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

"""Utility functions
"""

# Imports

# Sys
import time
import textwrap
import uuid

# Django
from django.conf import settings
from django.http import Http404

# Mail
from email import encoders
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage
from email import message_from_file

from hlimap import ImapServer

HAS_SMTP_SSL = False
try:
    from smtplib import SMTP
    from smtplib import SMTP_SSL
    HAS_SMTP_SSL = True
except ImportError:
    from smtplib import SMTP


def serverLogin(request):
    """Login to the server
    """
    # Login to the server:
    M = ImapServer(host=request.session['host'], port=request.session['port'],
                   ssl=request.session['ssl'])

    try:
        M.login(request.session['username'],
                request.session['password'])
        return M
    except:
        # TODO: The server can for some reason fail to login the user during a
        # normal session.
        # An exception should be raised here descriptive enough of what's
        # going on. Gmail's imap can for instance answer all requests with:
        #  NO [ALERT] Too many simultaneous connections. (Failure)
        raise Http404


def join_address_list(addr_list):
    '''Returns a comma separated list of mail addresses.

    @param addr_list: a list of addresses on the form [ ("name","email"), ... ]

    @return: comma separated list of addresses on a string.
    '''
    if not addr_list:
        return ''
    addrs = []
    for addr in addr_list:
        addrs.append(mail_addr_str(addr))

    return ','.join(addrs)


def mail_addr_str(mail_addr):
    '''String representation of a mail address.

    @param mail_addr: a tuple in the form ("Name", "email address")

    @return: '"Name" <email address>' or only '<email address>' if there is no
        name.
    '''
    if mail_addr[0]:
        return '"%s" <%s>' % (mail_addr[0], mail_addr[1])
    else:
        return '<%s>' % mail_addr[1]


def mail_addr_name_str(mail_addr):
    '''String representation of the person name in a mail address.

    @param mail_addr: a tuple in the form ("Name", "email address")

    @return: '"Name"' or '<email address>' if there is no name.
    '''
    if mail_addr[0]:
        return '%s' % mail_addr[0]
    else:
        return '<%s>' % mail_addr[1]


def quote_wrap_lines(text, quote_char='>', width=60):
    '''Wraps and quotes a message text.split

    @param text: text of the message
    @param quote_char: que character to be appended on eaxh line (without extra
        spaces)
    @param width: number of columns the text should have counting the
        quote_char

    @return: the quoted text.
    '''
    ln_list = text.split('\n')
    quote_char = '%s ' % quote_char
    width = width - len(quote_char)

    new_list = []
    for ln in ln_list:
        if len(ln) > width:
            ln = textwrap.fill(ln, width=width, initial_indent=quote_char,
                               subsequent_indent=quote_char)
            new_list.append(ln)
        else:
            new_list.append('%s %s' % (quote_char, ln))

    return '\n'.join(new_list)


def show_addrs(label, addr_list, default):
    '''Returns a text representation of the address list.
    '''
    txt = '%s: ' % label
    if addr_list:
        for addr in addr_list:
            txt += '%s, ' % mail_addr_str(addr)
        txt = txt[:-2] + '\n'
    else:
        if default:
            txt += '%s\n' % default
        else:
            return ''

    return txt

#
# Compose and send messages
#


def compose_rfc822(from_addr, to_addr, cc_addr, bcc_addr,
                   subject, message_plain, message_html, attachment_list=[],
                   headers=[]):
    '''
    Returns a rfc822 compliant message
    '''
    # Create the message text:
    if message_plain:
        message_plain = MIMEText(message_plain, _charset='utf-8')
    if message_html:
        message_html = MIMEText(message_html.encode('utf-8'),
                                _subtype='html', _charset='utf-8')

    if message_plain and message_html:
        msg_text = MIMEMultipart('alternative')
        msg_text.attach(message_plain)
        msg_text.attach(message_html)
    elif message_plain:
        msg_text = message_plain
    elif message_html:
        msg_text = message_html
    else:
        msg_text = MIMEText('', _charset='utf-8')

    # Include the attachments:
    if attachment_list.file_list:
        msg = MIMEMultipart('MIXED')
        msg.attach(msg_text)
        for attachment in attachment_list.file_list:
            filename = attachment.temp_file
            if attachment.media() == 'TEXT':
                fp = open(filename)
                # Note: we should handle calculating the charset
                attach = MIMEText(fp.read(),
                                  _subtype=attachment.media_subtype(),
                                  _charset='utf-8')
                fp.close()
            elif attachment.media() == 'IMAGE':
                fp = open(filename, 'rb')
                attach = MIMEImage(fp.read(),
                                   _subtype=attachment.media_subtype())
                fp.close()
            elif attachment.media() == 'AUDIO':
                fp = open(filename, 'rb')
                attach = MIMEAudio(fp.read(),
                                   _subtype=attachment.media_subtype())
                fp.close()
            elif (attachment.media() == 'MESSAGE' and
                    attachment.media_subtype() == 'RFC822'):
                fp = open(filename, 'r')
                attach = MIMEMessage(message_from_file(fp), 'RFC822')
                fp.close()
            else:
                fp = open(filename, 'rb')
                attach = MIMEBase(attachment.media(),
                                  attachment.media_subtype())
                attach.set_payload(fp.read())
                fp.close()

                # Encode the payload using Base64
                encoders.encode_base64(attach)

            # Set the filename parameter
            attach.set_param('name', attachment.filename)
            if attachment.show_inline:
                attach.add_header('Content-Disposition', 'inline',
                                  filename=attachment.filename)
            else:
                attach.add_header('Content-Disposition', 'attachment',
                                  filename=attachment.filename)
            if attachment.content_desc:
                attach.add_header('Content-Description',
                                  attachment.content_desc)
            if attachment.content_id:
                attach.add_header('Content-Id', attachment.content_id)

            msg.attach(attach)
    else:
        msg = msg_text

    if subject:
        msg['Subject'] = subject
    if from_addr:
        msg['From'] = from_addr
    if to_addr:
        msg['To'] = to_addr
    if cc_addr:
        msg['Cc'] = cc_addr
    if bcc_addr:
        msg['Bcc'] = bcc_addr

    msg['Date'] = (time.strftime('%a, %d %b %Y %H:%M:%S ', time.localtime()) +
                   '%+05d' % time.timezone)
    msg['X-Mailer'] = 'WebPyMail %s' % settings.WEBPYMAIL_VERSION

    # Message-ID header:
    if from_addr:
        host = from_addr.split('@')[-1]
        if host[-1] == '>':
            host = host[:-1]
    else:
        host = 'example.org'
    msg['Message-ID'] = '<%s@%s>' % (str(uuid.uuid4()), host)

    # Extra headers:
    if headers:
        for header in headers:
            msg[header] = headers[header]

    return msg


def send_mail(message,  smtp_host, smtp_port, user=None, passwd=None,
              security=None):
    '''
    Sends a message to a smtp server
    '''
    if security == 'SSL':
        if not HAS_SMTP_SSL:
            raise Exception('Sorry. '
                            'For SMTP_SSL support you need Python >= 2.6')
        s = SMTP_SSL(smtp_host, smtp_port)
    else:
        s = SMTP(smtp_host, smtp_port)
    # s.set_debuglevel(10)
    s.ehlo()

    if security == 'TLS':
        s.starttls()
        s.ehlo()
    if user:
        s.login(user, passwd)

    to_addr_list = []

    if message['To']:
        to_addr_list.append(message['To'])
    if message['Cc']:
        to_addr_list.append(message['Cc'])
    if message['Bcc']:
        to_addr_list.append(message['Bcc'])

    to_addr_list = ','.join(to_addr_list).split(',')

    s.sendmail(message['From'], to_addr_list, message.as_string())
    s.close()
