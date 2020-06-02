#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests.exceptions import HTTPError


class BrokerException(HTTPError, Exception):
    pass


class BrokerValidationException(ValueError):
    pass
