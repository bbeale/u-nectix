#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import get_returns, sort_returns
import tensorflow as tf


"""
https://towardsdatascience.com/how-to-write-a-profitable-strategy-for-algotrading-bitcoin-with-jesse-6c7064b22f1f
"""

class Predictor:

    def __init__(self, dataframe):

        self.sess           = tf.compat.v1.InteractiveSession()
        self.dataframe      = dataframe
        self.predictions    = dict()

    def get_securities_predictions(self):
        """Loop through tickers and run prediction algorithm."""
        for ticker in self.dataframe.keys():
            train, test = self.get_predictions(self.dataframe[ticker]['close'])
            self.predictions[ticker] = dict()
            self.predictions[ticker]['train'] = train
            self.predictions[ticker]['test'] = test
        return self.predictions

    def get_predictions(self, data):
        """Given a dataframe, return training and test data

        :param data:
        :return:
        """
        data = data.astype(float)
        size = 50
        returns = get_returns(data)

        # pass one of the above into sort_returns
        ins, outs = sort_returns(returns, size)

        div = int(.8 * ins.shape[0])
        train_ins, train_outs = ins[:div], outs[:div]
        test_ins, test_outs = ins[div:], outs[div:]

        x = tf.compat.v1.placeholder(tf.float32, [None, size])
        y_ = tf.compat.v1.placeholder(tf.float32, [None, 1])

        # we define trainable variables for our model
        W = tf.Variable(tf.random.normal([size, 1]))
        b = tf.Variable(tf.random.normal([1]))

        # we define our model: y = W*x + b
        y = tf.matmul(x, W) + b

        # MSE:
        cost = tf.reduce_sum(tf.pow(y - y_, 2)) / (2 * 1000)
        optimizer = tf.compat.v1.train.GradientDescentOptimizer(0.5).minimize(cost)

        # initialize variables to random values
        init = tf.compat.v1.global_variables_initializer()
        self.sess.run(init)
        # run optimizer on entire training data set many times
        for epoch in range(20000):
            self.sess.run(optimizer, feed_dict={x: train_ins, y_: train_outs.reshape(1, -1).T})
            # every 1000 iterations record progress
            if (epoch + 1) % 1000 == 0:
                c = self.sess.run(cost, feed_dict={x: train_ins, y_: train_outs.reshape(1, -1).T})
                print('Epoch:', '%04d' % (epoch + 1), 'cost=', '{:.9f}'.format(c))

        # train
        predict = y
        p = self.sess.run(predict, feed_dict={x: train_ins})
        position = 2 * ((p > 0) - .5)
        train_returns = position.reshape(-1) * train_outs
        # plot(np.cumprod(returns + 1))

        # test
        predict = y
        p = self.sess.run(predict, feed_dict={x: test_ins})
        position = 2 * ((p > 0) - .5)
        test_returns = position.reshape(-1) * test_outs

        return train_returns, test_returns

