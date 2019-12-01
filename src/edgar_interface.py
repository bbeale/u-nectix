#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter
from lib.edgar import (
    download_xml,
    calculate_transaction_amount,
    calculate_8k_transaction_amount,
)

import requests
import json
import time


class EdgarInterface:

    def __init__(self, edgar_token, dataframe=None):

        if not edgar_token or edgar_token is None:
            raise ValueError("[!] Edgar token required for API access")

        self.base_url       = "https://api.sec-api.io"
        self.token          = edgar_token
        self.api            = "{}?token={}".format(self.base_url, self.token)
        self.dataframe      = dataframe
        self.edgar_scores   = dict()

    def get_edgar_signals(self):
        """Loop through tickers and append EDGAR signals to that ticker's dataframe"""
        if not self.dataframe or self.dataframe is None:
            raise NotImplementedError("[!] Dataframe should only be none if AssetSelector is using it")

        for ticker in self.dataframe.keys():
            fdate = self.dataframe[ticker]["time"].iloc[-7].strftime("%Y-%m-%d")
            tdate = time_formatter(time.time(), time_format="%Y-%m-%d")
            self.edgar_scores[ticker] = self.calculate_edgar_signal(ticker, fdate, tdate)
        return self.edgar_scores

    def get_sec_filings(self, ticker, from_date, to_date, form_type=None, start=0, size=100):
        """Given a ticker symbol, a date range, and a form type, get SEC filings during that time.

        :param ticker:
        :param from_date:
        :param to_date:
        :param form_type:
        :param start:
        :param size:
        :return:
        """
        if not ticker or ticker is None:
            raise ValueError("[!] Invalid ticker")

        if not from_date or from_date is None:
            raise ValueError("[!] From date required")

        if not to_date or to_date is None:
            raise ValueError("[!] To date required")

        if not form_type or form_type is None:
            form_type = "8-K"       # Default to 8-K if None

        # construct the filter
        filter_8k = "ticker:\"%s\" AND formType:\"%s\" AND filedAt:{%s TO %s}" % (ticker, form_type, from_date, to_date)
        sort = [{"filedAt": {"order": "desc"}}]
        payload = {
            "query": {"query_string": {"query": filter_8k}},
            "from": start,
            "size": size,
            "sort": sort
        }
        resp = None
        try:
            resp = requests.post(self.api, json.dumps(payload), headers={"Content-Type": "application/json; charset=utf-8"}).json()
        except requests.HTTPError as httpe:
            print(httpe, "- Unable to submit API request. Retrying...")
            time.sleep(3)
            try:
                resp = requests.post(self.api, json.dumps(payload), headers={"Content-Type": "application/json; charset=utf-8"}).json()
            except requests.HTTPError as httpe:
                print(httpe, "- Unable to submit API request.")
        finally:
            return resp

    def calculate_edgar_signal(self, ticker, from_date, to_date):
        """Calculate edgar signal given a ticker symbol and a date range.

        Calculations come from data scraped from filings during that date range.

        :param ticker:
        :param from_date:
        :param to_date:
        :return:
        """
        if not ticker or ticker is None:
            raise ValueError("[!] Invalid ticker")

        if not from_date or from_date is None:
            raise ValueError("[!] From date required")

        if not to_date or to_date is None:
            raise ValueError("[!] To date required")

        resp = self.get_sec_filings(ticker, from_date, to_date).text
        r_dict = json.loads(resp)

        if r_dict["total"] is 0:
            return None

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
                print("[!] Unable to generate signal from SEC filings")
                continue

        return signal
