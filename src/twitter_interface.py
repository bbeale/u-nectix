#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter
import configparser
import nltk
import sys
import os

config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("../config.ini"))
except FileExistsError as e:
    print("FileExistsError: {}".format(e))
    sys.exit(1)


class TwitterInterface:

    def __init__(self, twitter_api_interface, dataframe):

        nltk.download('vader_lexicon')

        self.api        = twitter_api_interface
        self.dataframe  = dataframe
        self.tweets     = dict()

    def get_ticker_tweets(self):
        """Loop through tickers and return text from recent Twitter history."""
        for ticker in self.dataframe.keys():
            self.tweets[ticker] = self.get_tweets(ticker)
        return self.tweets

    def get_tweets(self, ticker, search_terms=None):
        """Get tweets about a ticker

        :param ticker:
        :param search_terms: optional additional search term
        :return: string consisting of text from tweets
        """
        if not search_terms or search_terms is None:
            query = "{} stock".format(ticker)
        else:
            query = "{} stock {}".format(ticker, search_terms)

        results = self.api.GetSearch(query, result_type="recent")

        result_dicts    = [dict(
            created_at  = time_formatter(float(result.created_at_in_seconds)),
            user        = result.user.name,
            text        = result.text
        ) for result in results if "RT" not in result.text]

        texts           = [res["text"] for res in result_dicts]
        text            = "\n\n".join(texts)

        return text
