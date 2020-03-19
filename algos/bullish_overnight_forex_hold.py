#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.broker import BrokerException
from util import time_from_datetime
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import statistics


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    if args.pair is None:
        args.pair = "USDEUR"
    if args.mode is None:
        args.mode = 'long'
    if args.period is None:
        args.period = "1D"
    if args.algorithm is None:
        args.algorithm = "bullish_overnight_forex_hold"
    if args.testperiods is None:
        args.testperiods = 30

    pass
