from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import clear_output

train_dataset = 'https://storage.googleapis.com/tf-datasets/titanic/train.csv'
test_dataset = 'https://storage.googleapis.com/tf-datasets/titanic/eval.csv'
print("TensorFlow version:", tf.__version__)

dftrain = pd.read_csv(train_dataset)            # Reading CSV file (xlx) => data frame
dftest = pd.read_csv(test_dataset)

sex_column = dftrain['sex']                     # Extracting specific column and return new array
age_data = dftrain.pop('age')                   # Removing specific column from the dataset and return new array
survived_data = dftrain.pop('survived')
survived_data_test = dftest.pop('survived')
first_row_age_data = age_data[0]

rows = dftrain.head(3)                          # Fetch rows by number

specific_row = dftrain.loc[2]                   # Extracting specific row

description = dftrain.describe()                # Fetch some info about the dataframe

dataset_shape = dftrain.shape                   # dataset shape (627, 9) -> (rows, columns)

gender_type = dftrain['sex'].unique()           # Fetch new array with the unique values ['male', 'female']

CATEGORICALS_COLUMS = ['sex', 'class']
NUMERIC_COLUMS = ['age', 'fare']

feature_columns = []
for feature_name in CATEGORICALS_COLUMS:
    vocabulary = dftrain[feature_name].unique()
    # print(vocabulary)
    feature_columns.append(tf.feature_column.categorical_column_with_vocabulary_list(feature_name, vocabulary))


for feature_name in NUMERIC_COLUMS:
    feature_columns.append(tf.feature_column.numeric_column(feature_name, dtype=tf.float32))


print(feature_columns)
# [
# VocabularyListCategoricalColumn(key = 'sex', vocabulary_list = ('male', 'female'), dtype = tf.string, default_value = -1, num_oov_buckets = 0),
# VocabularyListCategoricalColumn(key = 'class', vocabulary_list = ('Third', 'First', 'Second'), dtype = tf.string, default_value = -1, num_oov_buckets = 0), 
# NumericColumn(key = 'age', shape = (1, ), default_value = None, dtype = tf.float32, normalizer_fn = None), 
# NumericColumn(key = 'fare', shape = (1, ), default_value = None, dtype = tf.float32, normalizer_fn = None)
# ]


# Tensorflow model requires that the data we pass in comes as a Dataset Object - for this we need to convert our dataframe
def make_input_fn(dataframe, label_df, num_epochs=10, shuffle=True, batch_size=32):
    def input_function():
        # Create a dataset object from dict and its labels
        ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), label_df))
        if shuffle:
            # Randomize order of data for the model
            ds = ds.shuffle(1000)
        # Split data into batches (Feeding our model by batches)
        ds = ds.batch(batch_size).repeat(num_epochs)
        return ds
    return input_function

train_input_fn = make_input_fn(dftrain, survived_data)
eval_input_fn = make_input_fn(dftest, survived_data_test, num_epochs=1, shuffle=False)

# linear_estimate = tf.estimator.LinearClassifier(feature_columns=feature_columns)