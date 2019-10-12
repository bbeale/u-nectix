#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import requests
import time
import re


def compress_filings(filings):
    """Get a smaller data set (for testing).

    :param filings:
    :return:
    """
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


def download_xml(url, tries=1):
    """Download the XML version of the filing. If it fails wait for 5, 10, 15, ... seconds and try again.

    :param url:
    :param tries:
    :return:
    """
    try:
        response = requests.get(url)        # urllib.request.urlopen(url)
    except requests.exceptions.HTTPError as httpe:
        print(httpe, "Something went wrong. Wait for 5 seconds and try again.", tries)
        if tries < 5:
            time.sleep(5 * tries)
            download_xml(url, tries + 1)
    else:
        print("Document URL:\t", url)

        # decode the response into a string
        data = response.text
        # set up the regular expression extractoer in order to get the relevant part of the filing
        matcher = re.compile('<\?xml.*ownershipDocument>', flags=re.MULTILINE | re.DOTALL)
        matches = matcher.search(data)
        # the first matching group is the extracted XML of interest
        doc = matches.group(0) if matches is not None else None
        # instantiate the XML object
        root = ET.fromstring(doc) if doc is not None else None
        return root


def calculate_transaction_amount(xml):
    """Calculate the total transaction amount in $ of a giving form 4 in XML.

    :param xml:
    :return:
    """
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


def calculate_8k_transaction_amount(xml):
    """Calculate the total transaction amount in $ of a giving form 8-K in XML.

    :param xml:
    :return:
    """
    total = 0

    if xml is None:
        return total

    # is the owner a 10 percent shareholder?
    ownerpattern = "./reportingOwner/reportingOwnerRelationship/isTenPercentOwner"
    owner_holds_10_percent = True if int(xml.find(ownerpattern).text) > 0 else False
    non_derivative_transactions = xml.findall("./nonDerivativeTable/nonDerivativeTransaction")
    init_shares = None
    total_shares = None
    for t in non_derivative_transactions:
        # D for disposed or A for acquired
        action = t.find('./transactionAmounts/transactionAcquiredDisposedCode/value').text
        # number of shares disposed/acquired
        shares = t.find('./transactionAmounts/transactionShares/value').text
        # shares following the transaction
        post_shares = t.find('./postTransactionAmounts/sharesOwnedFollowingTransaction/value').text
        # number of shares prior to the transaction - initally None
        if init_shares is None:
            init_shares = float(shares) + float(post_shares)

        if total_shares is None:
            total_shares = init_shares

        else:
            total_shares -= float(shares)

    percent_traded = (float(total_shares)/float(init_shares))
    return init_shares, total_shares, percent_traded, owner_holds_10_percent


def add_non_derivative_transaction_amounts(filings):
    """Download the XML for each filing

    Calculate the total transaction amount per filing

    Save the calculate transaction value to the filing dict with key 'nonDerivativeTransactions'

    # TODO: customize this for 8-K

    :param filings:
    :return:
    """

    for filing in filings:
        url = filing['linkToTxt']
        xml = download_xml(url)
        nonDerivativeTransactions = calculate_transaction_amount(xml)
        filing['nonDerivativeTransactions'] = nonDerivativeTransactions
    return filings


def bs_xml_parse(url, tries=1):
    """Version of download_xml using BeautifulSoup. Clearly naming conventions aren't a thing.

    This function is in progress and may never get finished because it isn't a super high priority.

    :param url:
    :param tries:
    :return:
    """
    docs = []

    try:
        response = requests.get(url)
    except requests.exceptions.HTTPError as httpe:
        print(httpe, "Something went wrong. Wait for 5 seconds and try again.", tries)
        if tries < 5:
            time.sleep(5 * tries)
            bs_xml_parse(url, tries + 1)

    else:
        doc = response.text
        soup = BeautifulSoup(doc, 'xml')

        # grab all xml formatted documents
        filings = soup.find_all("ownershipDocument")
        for filing in filings:
            print(type(filing), filing)
            docs.append({filing["name"].text: filing})

        for doc in docs:
            # grab relevant tags from ownershipDocument
            soup = BeautifulSoup(doc, 'xml')
            issuer = soup.find("issuer")
            reporting_owner = soup.find("reportingOwner/rptOwnerName")
            non_derivative_transaction = soup.find_all("nonDerivativeTransaction")

            for ndt in non_derivative_transaction:
                print("P: ", ndt.text)
