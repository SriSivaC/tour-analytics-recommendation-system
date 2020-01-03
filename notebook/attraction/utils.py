'''
Utility class with some helper functions
'''

import pandas as pd
import numpy as np
import random
import os


class Util(object):
    def read_data(self, sparkSession, filepath):
        '''
        Function to read data required to
        build the recommender system
        '''
        print("Reading the data from " + filepath)
        return sparkSession.read.parquet(filepath).toPandas()

    def clean_subset(self, ratings, num_rows):
        '''
        Function to clean and subset the data according
        to individual machine power
        '''
        print("Extracting " + str(num_rows) + " rows from ratings")
        return ratings.iloc[:num_rows, :]

    def preprocess(self, ratings):
        '''
        Preprocess data for feeding into the network
        '''
        print("Preprocessing the dataset")
        unique_att = ratings.activityId.unique()
        unique_att.sort()

        att_index = [i for i in range(len(unique_att))]
        rbm_att_df = pd.DataFrame(list(zip(att_index, unique_att)), columns=['rbm_att_id', 'activityId'])

        joined = ratings.merge(rbm_att_df, on='activityId')
        joined = joined[['user_id', 'activityId', 'rbm_att_id', 'rating']]
        readers_group = joined.groupby('user_id')

        total = []
        for readerID, curReader in readers_group:
            temp = np.zeros(len(ratings))
            for num, book in curReader.iterrows():
                temp[book['rbm_att_id']] = book['rating']/5.0
            total.append(temp)

        return joined, total

    def split_data(self, total_data):
        '''
        Function to split into training and validation sets
        '''
        print("Free energy required, dividing into train and validation sets")
        random.shuffle(total_data)
        n = len(total_data)
        print("Total size of the data is: {0}".format(n))
        size_train = int(n * 0.75)
        X_train = total_data[:size_train]
        X_valid = total_data[size_train:]
        print("Size of the training data is: {0}".format(len(X_train)))
        print("Size of the validation data is: {0}".format(len(X_valid)))
        return X_train, X_valid

    def free_energy(self, v_sample, W, vb, hb):
        '''
        Function to compute the free energy
        '''
        wx_b = np.dot(v_sample, W) + hb
        vbias_term = np.dot(v_sample, vb)
        hidden_term = np.sum(np.log(1 + np.exp(wx_b)), axis=1)
        return -hidden_term - vbias_term
