from django.db import models
from django.utils.translation import ugettext

from django.contrib.auth.models import User, Group

import rapidsms
from rapidsms.message import Message
from rapidsms.connection import Connection

import re, time, datetime

from models.base import Provider, MessageLog

from django.core.urlresolvers import RegexURLResolver, Resolver404
resolver = RegexURLResolver(r'', "apps.sms.sms")

from malnutrition.sms.command import HandlerFailed, FormFailed, authenticated, _
        
class App(rapidsms.app.App):
    MAX_MSG_LEN = 140

    def start (self):
        """Configure your app in the start phase."""
        pass

    def parse(self, message):
        provider = Provider.by_mobile(message.peer)
        if provider:
            message.sender = provider.user
        else:
            message.sender = None
        message.was_handled = False

    def cleanup(self, message):
        log = MessageLog(mobile=message.peer,
                         sent_by=message.sender,
                         text=message.text,
                         was_handled=message.was_handled,
                         form_error=getattr(message, "form_failed", False))
        log.save()

    def handle(self, message):
        try:
            callback, callback_args, callback_kwargs = resolver.resolve(message.text.lower())
        except Resolver404:
            raise ValueError, "There was no view found for: %s" % message.text


        message.was_handled = True
        message.form_failed = False
        try:
            res = callback(message, *callback_args, **callback_kwargs)
            if callable(res):
                res = res()
            return message.respond(res)
        except FormFailed, e:
            # parsing the form failed
            message.form_failed = True
            return message.respond(e.message)
        except HandlerFailed, e:
            # processing the form failed
            return message.respond(e.message)
        except:
            raise