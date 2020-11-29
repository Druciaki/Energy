#
# @author: Thiago Druciaki Casagrande
#
# Read TSV input file and serves data as np arrays
#
 
import os, sys
from sklearn.datasets.base import Bunch
import numpy as np
import pdb;

class energy_file:
    efile = None
    lines_count = 0
    columns_count = 0
    filters = []
    date_column_index = 0 # Always expect date to be on the first column
    data_indexes = [] # relevant data to be analized (after filter is applied)
    data = []

    def __init__(self, name=''):
        self.efile = open(name)

    def normalize_value(self, value):
        ''' remove dots and use ',' as '.'
            this functions must be called depending on how data (number) is formated
        '''
        ret = value.replace('.','')
        ret = ret.replace(',','.')
        return float(ret)

    def normalize_date(self, date):
        ''' Turn DD/MM/YYYY into YYYYMMDD - so that any kind of sorting result on a cronological order
        '''
        new_age = date.split("/")
        new_date = new_age[2]+new_age[1]+new_age[0]
        return int(new_date)

    def readLines(self, data_filter = None):
        ''' data_filter may receive an array with the headers that must be read
            i.e. ["NE","N"]
        '''
        lins = self.efile.read().split('\n')
        self.lines_count = len(lins)
        headers = lins[0].split('\t')
        self.date_column_index = headers.index('DATA')
        if data_filter:
            for df in data_filter:
                self.data_indexes.append(headers.index(df))
        else:
            for i in range(1,len(headers)):
                self.data_indexes(i)

        data_array = []
        lins.pop(0)

        dates = []
        values = []
        for info in lins:
            info = info.split('\t')
            value = 0.0
            for x in self.data_indexes:
                value += self.normalize_value(info[x])

            dates.append(self.normalize_date(info[0]))
            values.append(value)

        self.data.append(dates)
        self.data.append(values)

    def get_data(self):
        if not self.data:
            self.readLines()
        return self.data

    def get_numpy_data(self):
        raw = self.get_data()
        return {'dates':np.asarray(raw[0]), 'values':np.asarray(raw[1])}


