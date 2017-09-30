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

    def prepare(self, header, content, msg_type='plain'):
        if header == '':
            print('%s\n', 'Header cannot be empty')
            return
        if content == '':
            print('%s\n', 'Content cannot be empty')
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


class Email_from_conf(object):
    def __init__(self, path='etc/conf.json'):
        print('Begin')
        self._settings = self.get_settings (path)
        print('Reading successful')
        self.proceed()

    def proceed(self):
        try:
            print('Mail prep')
            mail = Email(
                    self._settings['sender'],
                    self._settings['receiver'],
                )
            mail.prepare(
                    self._settings['header'],
                    self._settings['content'],
                    self._settings['type']
                )
            print('Mail sending')
            mail.send(
                    self._settings['smtp_addr'],
                    self._settings['login'],
                    self._settings['password']
                )
            print('Sending successful')
        except KeyError:
            exit("Incorrect config file")

    def get_settings(self, path):
        print('File reading')
        try:
            with open(path, 'r') as conf:
                return load(conf)
        except FileNotFoundError:
            err_msg = 'Error - Incorrect path to config file: ' 
            err_msg+= path
            exit(err_msg)


def usage_sample() :
    header = 'Python mail'
    message = '''
    Hi, 
    
    This mail was sent using a Python script.

    Cheers !
    '''

    mail = Email(
            'sender@mail.com',
            'receiver@mail.com'
        )
    mail.prepare(
            header,
            message
        )

    mail.send(
            'smtp.server.addr',
            'login@mail.com',
            'password'
        )

if __name__ == '__main__':
    usage_sample()
