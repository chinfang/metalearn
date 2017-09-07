import time

import numpy as np

from common_operations import *
from simple_metafeatures import get_simple_metafeatures
from statistical_metafeatures import get_statistical_metafeatures
from information_theoretic_metafeatures import get_information_theoretic_metafeatures

class MetaFeatures():

    def __init__(self):
        self.metafeatures = {}
        self.valid_intype = 'dict'
        self.valid_outtype = 'array2+names'

    def fit(self, intype, data, labels=None):
        if self._validate_inputs(intype, data, labels):
            self._update_metafeatures(data, labels)

    def predict(self, outtype, data=None):
        if outtype == self.valid_outtype:
            features = []
            values = []
            values.append([])
            for feature in self.metafeatures:
                features.append(feature)
                value = self.metafeatures[feature]
                values[0].append(value)
            output = [features, values]
            return output
        else:
            return None

    def _validate_inputs(self, intype, data, labels):
        if intype == self.valid_intype and labels != None:
            num_instances = len(labels)
            for attribute in data:
                column = data[attribute]
                if len(column) != num_instances:
                    return False
            return True
        return False

    """
    Compute and store metafeatures using labelled data

    Parameters
    ----------
    inputs: dict of feature names (key) and arrays of values (value)
            all arrays must have the same length
    labels: array of labels of the above inputs. must have same length as above inputs

    Returns
    -------
    n/a
    """
    def _update_metafeatures(self, inputs, labels):
        start_time = time.process_time()

        X = None
        attributes = []
        for attribute in inputs:
            column = np.array(inputs[attribute])
            column = column.reshape(column.shape[0], -1)
            attributes.append((attribute, str(type(column[0,0]))))
            if X == None:
                X = np.array(column, dtype = 'object')
            else:
                X = np.append(X, column, axis = 1)
        attributes.append(('class', list(set(labels))))
        Y = np.array(labels)
        data = np.append(X, Y.reshape(Y.shape[0], -1), axis = 1)

        # Drop instances that have missing data
        data = data[(data != np.array(None)).all(axis=1)]

        data_numeric_without_class = replace_nominal(data[:,0:-1], attributes)
        data_preprocessed = np.append(normalize(data_numeric_without_class), data[:,-1].reshape(data.shape[0],1), axis = 1)

        self.metafeatures.update(get_simple_metafeatures(attributes, data, Y))
        self.metafeatures.update(get_statistical_metafeatures(attributes, data, data_preprocessed))
        self.metafeatures.update(get_information_theoretic_metafeatures(attributes, data, X, Y))
        self.metafeatures['total_time'] = time.process_time() - start_time