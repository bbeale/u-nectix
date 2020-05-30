#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

class SentimentAnalysisException(Exception):
    pass

class SentimentAnalysis:

    def __init__(self, dataframe=None, texts=None):

        nltk.download('vader_lexicon')
        if dataframe is not None:
            self.dataframe = dataframe
        if texts is not None:
            self.texts = texts

        self.sid = SentimentIntensityAnalyzer()
        self.sentiments = dict()

    def get_sentiments(self):
        """Loop through tickers and calculate a sentiment score based on Twitter history."""
        for ticker in self.texts.keys():
            self.sentiments[ticker] = self.get_sentiment(ticker)
        return self.sentiments

    @staticmethod
    def get_sentiment(text):
        """Given a text block, return a sentiment score based.

        :param text:
        :return:
        """
        sid = SentimentIntensityAnalyzer()
        try:
            text_polarity = sid.polarity_scores(text)
        except SentimentAnalysisException:
            raise SentimentAnalysisException('[!] Unable to calculate polarity scores for this text element.')
        else:
            if text_polarity['compound'] > 0:
                sentiment   = 'positive'

            else:
                sentiment   = 'negative'

            return sentiment
