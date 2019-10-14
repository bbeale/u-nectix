#!/usr/bin/env python
# -*- coding: utf-8 -*-
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk


class SentimentAnalysis:

    def __init__(self, dataframe, texts):

        nltk.download('vader_lexicon')

        self.sid        = SentimentIntensityAnalyzer()
        self.dataframe  = dataframe
        self.texts      = texts
        self.sentiments = dict()

    def get_sentiments(self):
        """Loop through tickers and calculate a sentiment score based on Twitter history."""
        for ticker in self.texts.keys():
            self.sentiments[ticker] = self.get_sentiment(ticker)
        return self.sentiments

    def get_sentiment(self, text):
        """Given a text block, return a sentiment score based.

        TODO: Make this look up tweets by date range vs relying on result_type="recent"

        ALSO TODO: Move this to SentimentAnalysis class
            - this class should only interface with Twitter
            - sentiment analysis should not care where the text comes from
            - sentiment analysis should occur whether given tweets or other sources
            - prep tweet results for sent. analysis here but don't do the actual analysis

        :param text:
        :return:
        """
        text_polarity   = self.sid.polarity_scores(text)

        if text_polarity["compound"] > 0:
            sentiment   = "positive"

        else:
            sentiment   = "negative"

        return sentiment
