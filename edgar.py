#!/usr/bin/env python
# -*- coding: utf-8 -*-
# %%

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
from spacy import displacy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib

import urllib.request
import configparser
import requests
import spacy
import nltk
import json
import sys
import os
# %matplotlib inline

nlp = spacy.load("en_core_web_lg")
nltk.download("vader_lexicon")
config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("config.ini"))
except FileExistsError as e:
    print("File exists error: {}".format(e))
    sys.exit(1)

# %%

# API Key
TOKEN = config["edgar"]["TOKEN"]
# API endpoint
BASE_URL = config["edgar"]["URL"]
API = "{}?token={}".format(BASE_URL, TOKEN)

# Define the filter parameters
filter = "formType:\"8-k\" AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:[2019-08-01 TO " \
         "2019-09-02]"
# Start with the first filing. Increase it when paginating.
# Set to 10000 if you want to fetch the next batch of filings. Set to 20000 for the next and so on.
start = 0
# Return 10,000 filings per API call
size = 10000
# Sort in descending order by filedAt
sort = [{"filedAt": {"order": "desc"}}]

payload = {
    "query": {"query_string": {"query": filter}},
    "from": start,
    "size": size,
    "sort": sort
}

# Format your payload to JSON bytes
jsondata = json.dumps(payload)
jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes

# Instantiate the request
req = urllib.request.Request(API)

# Set the correct HTTP header: Content-Type = application/json
req.add_header('Content-Type', 'application/json; charset=utf-8')
# Set the correct length of your request
req.add_header('Content-Length', len(jsondataasbytes))

# Send the request to the API
response = urllib.request.urlopen(req, jsondataasbytes)

# Read the response
res_body = response.read()
# Transform the response into JSON
filingsJson = json.loads(res_body.decode("utf-8"))

# %%

# Print the response. Most likely this will throw an error because we fetched a
# large amount of data (10,000 filings). Reduce the number of filings and you will see a result here.
print(json.dumps(filingsJson, indent=2))

# %%

# Show us how many filings matched our filter criteria.
# This number is most likely different from the number of filings returned by the API.
print(filingsJson['total'])

# %%


def compress_filings(filings):
    store = {}
    compressed_filings = []
    for filing in filings:
        filedAt = filing['filedAt']
        if filedAt in store and store[filedAt] < 5:
            compressed_filings.append(filing)
            store[filedAt] += 1
        elif filedAt not in store:
            compressed_filings.append(filing)
            store[filedAt] = 1
    return compressed_filings


# %%

filings = compress_filings(filingsJson['filings'])
filings

# %%

import xml.etree.ElementTree as ET
import re
import time


# Download the XML version of the filing. If it fails wait for 5, 10, 15, ... seconds and try again.
def download_xml(url, tries=1):
    try:
        response = urllib.request.urlopen(url)
    except:
        print('Something went wrong. Wait for 5 seconds and try again.', tries)
        if tries < 5:
            time.sleep(5 * tries)
            download_xml(url, tries + 1)
    else:
        # decode the response into a string
        data = response.read().decode('utf-8')
        # set up the regular expression extractoer in order to get the relevant part of the filing
        matcher = re.compile('<\?xml.*ownershipDocument>', flags=re.MULTILINE | re.DOTALL)
        matches = matcher.search(data)
        # the first matching group is the extracted XML of interest
        xml = matches.group(0)
        # instantiate the XML object
        root = ET.fromstring(xml)
        print(url)
        return root


# %%


# Calculate the total transaction amount in $ of a giving form 4 in XML
def calculate_transaction_amount(xml):
    total = 0

    if xml is None:
        return total

    nonDerivativeTransactions = xml.findall("./nonDerivativeTable/nonDerivativeTransaction")

    for t in nonDerivativeTransactions:
        # D for disposed or A for acquired
        action = t.find('./transactionAmounts/transactionAcquiredDisposedCode/value').text
        # number of shares disposed/acquired
        shares = t.find('./transactionAmounts/transactionShares/value').text
        # price
        priceRaw = t.find('./transactionAmounts/transactionPricePerShare/value')
        price = 0 if priceRaw is None else priceRaw.text
        # set prefix to -1 if derivatives were disposed. set prefix to 1 if derivates were acquired.
        prefix = -1 if action == 'D' else 1
        # calculate transaction amount in $
        amount = prefix * float(shares) * float(price)
        total += amount

    return round(total, 2)

# %%

# Test the calc function by using just one filing
url = 'https://www.sec.gov/Archives/edgar/data/1592176/0000706688-19-000155.txt'
xml = download_xml(url)
amount = calculate_transaction_amount(xml)
amount

# %%


# Download the XML for each filing
# Calculate the total transaction amount per filing
# Save the calculate transaction value to the filing dict with key 'nonDerivativeTransactions'
def add_non_derivative_transaction_amounts():
    for filing in filings:
        url = filing['linkToTxt']
        xml = download_xml(url)
        nonDerivativeTransactions = calculate_transaction_amount(xml)
        filing['nonDerivativeTransactions'] = nonDerivativeTransactions


# %%

# Let's inspect filings and ensure that the new key 'nonDerivativeTransactions' is set
# docs: https://sec-api.io/docs#introduction

# %%

docs = []
for filing in filings:
    url = filing['linkToHtml']
    r = requests.get(url).text
    docs.append(r)

for doc in docs:
    soup = BeautifulSoup(doc, 'html.parser')
    paras = soup.find_all("p")
    for p in paras:
        print("P: ", p.text)
