#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter
import src.sentiment_analysis as sa
import configparser
import nltk
import time
import sys
import os

config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("../config.ini"))
except FileExistsError as e:
    print("FileExistsError: {}".format(e))
    sys.exit(1)

class TwitterInterfaceException(Exception):
    pass

class TwitterActionException(TwitterInterfaceException):
    pass

class TwitterInterface:

    def __init__(self, twitter_api_interface, dataframe):

        nltk.download('vader_lexicon')

        self.api        = twitter_api_interface
        self.dataframe  = dataframe
        self.tweets     = dict()

    def get_ticker_tweets(self):
        """Loop through tickers and return text from recent Twitter history."""
        for ticker in self.dataframe.keys():
            self.tweets[ticker] = self.get_tweets(self.api, ticker)
            self.tweets["{}_sent".format(ticker)] = self.get_tweet_sentiments(self.tweets[ticker])
        return self.tweets

    @classmethod
    def get_tweets(cls, api_interface, ticker, since=None, search_terms=None):
        """Get tweets about a ticker

        :param api_interface:
        :param ticker:
        :param since: YYYY-MM-DD formatted date
        :param search_terms: optional additional search term
        :return: string consisting of text from tweets
        """
        if not api_interface or api_interface is None:
            raise TwitterInterfaceException

        if not ticker or ticker is None:
            raise ValueError("Invalid ticker symbol")

        if not since or since is None:
            since = time_formatter(time.time() - (604800 * 13), time_format="%Y-%m-%d")

        if not search_terms or search_terms is None:
            query = "{} stock".format(ticker)
        else:
            query = "{} stock {}".format(ticker, search_terms)

        try:
            results = api_interface.GetSearch(query, result_type="recent", since=since, count=100)
        except TwitterActionException:
            raise TwitterActionException("[!] Failed to get Twitter search results for {}.".format(ticker))
        else:

            result_dicts    = [dict(
                created_at  = time_formatter(float(result.created_at_in_seconds)),
                user        = result.user.name,
                text        = result.text
            ) for result in results if "RT" not in result.text]

            texts           = [res["text"] for res in result_dicts]
            text            = "\n\n".join(texts)

            return text

    @staticmethod
    def get_tweet_sentiments(tweets):

        if len(tweets) is 0:
            raise ValueError("Tweets list cannot be empty.")

        result = dict()
        for tweet in tweets:
            sent = sa.get_sentiment(tweet)
            result[tweet] = sent

        return result   # TODO: test this
