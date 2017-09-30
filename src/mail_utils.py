# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# auhtor: Pierre Bouillon [https://github.com/pBouillon]

import email.mime.text
from email.mime.text import MIMEText

import json
from json import load

import smtplib
from smtplib import SMTP_SSL

import sys
from sys import exit


class Server(object):
    def __init__(self, smtp_addr, sender_addr, psswd):
        self._connection  = None
        self._sender_addr = sender_addr
        self._psswd     = psswd
        self._smtp_addr = smtp_addr

    def connect(self):
        try:
            self._connection = SMTP_SSL(self._smtp_addr)
            self._connection.set_debuglevel(True)
            self._connection.login(self._sender_addr, self._psswd)
        except Exception as e:  
            exit('Error: Unable to establish the connection')

    def send(self, sender, receiver, payload):
        if self._connection == None :
            exit('Error: No connection defined')
        try:
            self._connection.sendmail(sender, receiver, payload)
        except Exception as e:  
            exit('Error: Mail sending failed')
        finally:
            self._connection.close()


class Email(object):
    def __init__(self, sender, receiver):
        self._receiver = receiver
        self._msg    = None
        self._sender = sender 
        self._server = None

    @classmethod
    def send_from_source_file(cls, path = 'etc/config.json'):
        mail = cls('', '')
        settings = mail._get_settings_from(path)
        mail._send_from_conf(settings)

    def _get_settings_from(self, path):
        try:
            with open(path, 'r') as conf:
                return load(conf)
        except FileNotFoundError:
            err_msg = 'Error - Incorrect path to config file: ' 
            err_msg+= path
            exit(err_msg)

    def _send_from_conf(self, config):
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
            exit("Incorrect config file")

    def prepare(self, header, content, msg_type='plain'):
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
        if self._msg == None:
            exit('Error: Can\'t send an empty mail')
        self._server = Server(smtp_addr, sender_addr, psswd)
        self._server.connect()
        self._server.send(
                self._sender, 
                self._receiver,
                self._msg.as_string()
            )


if __name__ == '__main__':
    Email.send_from_source_file()