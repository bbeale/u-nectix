#!/usr/bin/env python
# -*- coding: utf-8 -*-
from broker import BrokerException


def run(broker, args):

    if not broker or broker is None:
        raise BrokerException("[!] A broker instance is required.")
    else:
        broker = broker

    if args.pair is None:
        args.pair = "USDEUR"
    if args.period is None:
        args.period = "1D"
    if args.algorithm is None:
        args.algorithm = "bullish_overnight_forex_hold"
    if args.testperiods is None:
        args.testperiods = 30

    pass
