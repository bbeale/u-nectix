#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alpaca_functions import time_formatter
from lib.edgar import (
    download_xml,
    calculate_transaction_amount,
    calculate_8k_transaction_amount,
    add_non_derivative_transaction_amounts
)

import requests
import json
import time


class EdgarInterface:

    def __init__(self, edgar_token, dataframe):

        if not edgar_token or edgar_token is None:
            raise ValueError("Edgar token required for API access")

        self.base_url       = "https://api.sec-api.io"
        self.token          = edgar_token
        self.api            = "{}?token={}".format(self.base_url, self.token)
        self.dataframe      = dataframe
        self.edgar_scores   = dict()

    def get_edgar_signals(self):
        """Loop through tickers and append EDGAR signals to that ticker's dataframe"""
        for ticker in self.dataframe.keys():
            fdate = self.dataframe[ticker]["time"].iloc[-7]
            tdate = time_formatter(time.time())
            self.edgar_scores[ticker] = self.calculate_edgar_signal(ticker, fdate, tdate)
        return self.edgar_scores

    def calculate_edgar_signal(self, ticker, from_date, to_date):
        """Calculate edgar signal given a ticker symbol and a date range.

        Calculations come from data scraped from filings during that date range.

        :param ticker:
        :param from_date:
        :param to_date:
        :return:
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker")

        if not from_date or from_date is None:
            raise ValueError("From date required")

        if not to_date or to_date is None:
            raise ValueError("To date required")

        filter_8k = "ticker:(\"%s\") AND formType:(\"8-K\") AND filedAt:{%s TO %s}" % (ticker, from_date, to_date)
        # filter_8k = "ticker:(\"%s\") AND formType:(\"8-K\")" % ticker
        sort = [{"filedAt": {"order": "desc"}}]
        start = 0
        size = 100

        payload = {
            "query": {"query_string": {"query": filter_8k}},
            "from": start,
            "size": size,
            "sort": sort
        }

        resp = requests.post(self.api, payload).text
        r_dict = json.loads(resp)
        signal = None
        total_traded = 0

        for item in r_dict["filings"]:
            xml = download_xml(item["linkToTxt"])
            amount = calculate_transaction_amount(xml)
            total_traded += amount

            initial, post, percenttraded, majorshareholder = calculate_8k_transaction_amount(xml)
            print("# pre:\t\t{}\t\t# post:\t\t{}\t\t% traded:\t\t{}".format(initial, post, percenttraded))

            if majorshareholder and initial > post:
                signal = "STRONGBEAR"

            elif not majorshareholder and initial > post:
                signal = "BEAR"

            elif majorshareholder and post > initial:
                signal = "STRONGBULL"

            elif not majorshareholder and initial > post:
                signal = "BULL"

            else:
                return "Unable to generate signal from SEC filings"

        return signal
