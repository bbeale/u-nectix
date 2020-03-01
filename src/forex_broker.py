#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests.exceptions import HTTPError
from src.broker import BrokerValidationException
import pandas as pd
import time


class ForexBroker:

    def __init__(self, api):

        if not api or api is None:
            raise BrokerValidationException("[!] API instancerequired.")

        self.api = api

    def get_account(self):
        raise NotImplementedError

    def get_trading(self):
        raise NotImplementedError
