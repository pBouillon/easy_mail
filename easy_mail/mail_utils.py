# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017 Pierre Bouillon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# author: Pierre Bouillon [https://github.com/pBouillon]

"""mail_utils

mail_utils define the Email class which will use Server to send
an email following the specs defined in a json file or added during
the execution of a script.
"""

import email.mime.text
from email.mime.application import MIMEApplication
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText

import easy_mail.mail_exceptions
from easy_mail.mail_exceptions import BadMailTypeException
from easy_mail.mail_exceptions import EmptyMailBodyException
from easy_mail.mail_exceptions import EmptyMailHeaderException
from easy_mail.mail_exceptions import EmptyPayloadException

import json
from json import load

import mimetypes
from mimetypes import guess_type

import os
from os import path

import smtplib
from smtplib import SMTP_SSL

import sys
from sys import exit

"""Constant : int
Must be at least x.x (3 char)
"""
MINIMAL_ATT_NAME = 3

class Email(object):
    """Mail builder

    Attributes:
        _receiver : destination of the mail
        _msg      : mail content
        _sender   : sender of the mail
        _server   : server address
    """
    def __init__(self, sender, receiver):
        self._receiver = receiver
        self._msg    = None
        self._sender = sender 
        self._server = None

    @classmethod
    def send_from_source_file(cls, path):
        """Sending mail using a file

        Arguments:
            path : (str) path to the json file
        """
        mail = cls('', '')
        settings = mail._get_settings_from(path)
        mail._send_from_conf(settings)

    def _get_settings_from(self, path):
        """Scan the config file and return its content

        Arguments:
            path: (str) path to the config file

        Raise:
            FileNotFoundError: raised if the file is missing
        """
        try:
            with open(path, 'r') as conf:
                return load(conf)
        except FileNotFoundError:
            err_msg = 'Error: Incorrect path to config file: ' 
            err_msg+= path
            exit(err_msg)

    def _send_from_conf(self, config):
        """Prepare and send the mail from the config

        Arguments:
            config: (dict) content of the config file

        Raise:
            KeyError: raised if an element is missing

        """
        try:
            mail = Email(
                    config['sender'],
                    config['receiver'],
                )
            mail.prepare(
                    config['header'],
                    config['content'],
                    config['type']
                )
            mail.send(
                    config['smtp_addr'],
                    config['login'],
                    config['password']
                )
        except KeyError:
            exit("Error: Incorrect config file")

    def prepare(self, header, content, msg_type='plain'):
        """Prepare the payload of the mail

        Arguments:
            header  : (str) title of the mail
            content : (str) main text of the mail
            msg_type: (str) type of the text (plain | html)
        
        Raise:
            BadMailTypeException   : raised if type != (plain | html)
            EmptyMailBodyException : raised if the content is empty
            EmptyMailHeaderException : raised if the header is empty
        """
        if header == '':
            raise EmptyMailHeaderException
        if content == '':
            raise EmptyMailBodyException
        if msg_type != 'plain' and msg_type != 'html':
            raise BadMailTypeException

        self._msg = MIMEMultipart()

        core = MIMEText(content)
        self._msg.preamble = header
        self._msg.attach(core)

        self._msg ['From'] = self._sender
        self._msg ['To']   = self._receiver
        self._msg ['Subject'] = header

    def add_attachments(self, paths):
        """Join attachments

        Parse all paths
        Then check the validity of the file
        Then check its type
        Then add it to the mail

        Arguments:
            paths : (Type[str]) paths to attachments
        
        Raise:
            BadFileNameException : raised if file name is too short
            FileDoesNotExistsException : raised if file does not exists
        """
        attchmt = None

        for file in paths:
            if len(file) < MINIMAL_ATT_NAME:
                raise BadFileNameException
            if not path.exists(file):
                raise FileDoesNotExistsException

            ctype, encoding = mimetypes.guess_type(file)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            main_type, sub_type = ctype.split('/', 1)

            attchmt = None
            with open(file, 'rb') as f:
                attchmt = MIMEBase(main_type, sub_type)
                attchmt.set_payload(f.read())
            encode_base64(attchmt)
            self._msg.add_header (
                    'Content-Disposition', 
                    'attachment',
                    filename=path.basename(file)
                )
            self._msg.attach(attchmt)

    def send(self, smtp_addr, sender_addr, psswd):
        """Send the mail

        Arguments:
            smtp_addr  : (str) server address
            sender_addr: (str) address used to send the mail
            psswd      : (str) password to establish the connection
        
        Raise:
            EmptyPayloadException: raised if self._msg isn't set
        """
        if self._msg == None:
            raise EmptyPayloadException

        self._server = Server(smtp_addr, sender_addr, psswd)
        self._server.connect()
        self._server.send(
                self._sender, 
                self._receiver,
                self._msg.as_string()
            )


class Server(object):
    """Informations and actions with the server

    Attributes:
        _connection : the current connection with the server
        _psswd      : password to establish the connection
        _sender_addr: address used with the password
        _smtp_addr  : server address
    """
    def __init__(self, smtp_addr, sender_addr, psswd):
        self._connection  = None
        self._psswd       = psswd
        self._sender_addr = sender_addr
        self._smtp_addr   = smtp_addr

    def connect(self):
        """Establish the connection

        Raise:
            Exception: every exception such as bad login or 
                       a connection lost
        """
        try:
            self._connection = SMTP_SSL(self._smtp_addr)
            self._connection.ehlo()
            self._connection.startttls()
            self._connection.ehlo()
            self._connection.login(self._sender_addr, self._psswd)
        except Exception:  
            exit('Error: Unable to establish the connection')

    def send(self, sender, receiver, payload):
        """send the message

        Arguments:
            sender  : (str) sender of the mail
            receiver: (str) destination of the mail
            payload : (str) MIMEText as string containing the
                            header and the main text

        Raise:
            TypeError: raised if the connection isn't set 
            Exception: every exception such as unknown address 
                       for either of the mail provided
        """
        try:
            self._connection.sendmail(sender, receiver, payload)
        except TypeError:
            exit('Error: No connection defined')
        except Exception:  
            exit('Error: Mail sending failed')
        finally:
            self._connection.close()
