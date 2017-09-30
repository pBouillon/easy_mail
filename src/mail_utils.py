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
# auhtor: Pierre Bouillon [https://github.com/pBouillon]

"""mail_utils

mail_utils define the Email class which will use Server to send
an email following the specs defined in a json file or added during
the execution of a script.
"""

import email.mime.text
from email.mime.text import MIMEText

import json
from json import load

import json.decoder
from json.decoder import JSONDecodeError

import smtplib
from smtplib import SMTP_SSL

import sys
from sys import exit


__version__ = '1.0.0'


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
            self._connection.set_debuglevel(True)
            self._connection.login(self._sender_addr, self._psswd)
        except Exception as e:  
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
    def send_from_source_file(cls, path = 'etc/config.json'):
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
            JSONDecodeError  : raised if the json file isn't 
                               correct
        """
        try:
            with open(path, 'r') as conf:
                return load(conf)
        except FileNotFoundError:
            err_msg = 'Error: Incorrect path to config file: ' 
            err_msg+= path
            exit(err_msg)
        except JSONDecodeError :
            exit('Error: Unable to decode the json file')

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
        """
        if header == '':
            exit('Error: Header cannot be empty')
            return
        if content == '':
            exit('Error: Content cannot be empty')
            return
        else: 
            self._msg = MIMEText(content, msg_type)
            self._msg ['From'] = self._sender
            self._msg ['To']   = self._receiver
            self._msg ['Subject'] = header

    def send(self, smtp_addr, sender_addr, psswd):
        """Send the mail

        Arguments:
            smtp_addr  : (str) server address
            sender_addr: (str) address used to send the mail
            psswd      : (str) password to establish the connection

        """
        if self._msg == None:
            exit('Error: Can\'t send an empty mail')
        self._server = Server(smtp_addr, sender_addr, psswd)
        self._server.connect()
        self._server.send(
                self._sender, 
                self._receiver,
                self._msg.as_string()
            )
