#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from alpaca_functions import time_formatter
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

        self.sid        = SentimentIntensityAnalyzer()
        self.api        = twitter_api_interface
        self.dataframe  = dataframe
        self.tweets     = None

    def get_twitter_sentiments(self):
        """Loop through tickers and calculate a sentiment score based on Twitter history."""
        for ticker in self.dataframe.keys():
            self.dataframe[ticker] = self.get_sentiment(ticker)

    def get_sentiment(self, ticker):
        """Given a ticker symbol, return a sentiment score based on recent tweets.

        TODO: Make this look up tweets by date range vs relying on result_type="recent"

        ALSO TODO: Move this to SentimentAnalysis class
            - this class should only interface with Twitter
            - sentiment analysis should not care where the text comes from
            - sentiment analysis should occur whether given tweets or other sources
            - prep tweet results for sent. analysis here but don't do the actual analysis

        :param ticker:
        :return:
        """
        results = self.api.GetSearch("{} stock".format(ticker), result_type="recent")

        result_dicts = [dict(
            created_at=time_formatter(float(result.created_at_in_seconds)),
            user=result.user.name,
            text=result.text
        ) for result in results if "RT" not in result.text]

        texts = [res["text"] for res in result_dicts]
        text = "\n\n".join(texts)

        text_polarity = self.sid.polarity_scores(text)

        if text_polarity["compound"] > 0:
            sentiment = "positive"

        else:
            sentiment = "negative"

        return sentiment
