#
# @author: Thiago Druciaki Casagrande
#
# usage: python energyloaddemand.py <FILE.[CSV,TSV]> <#years>
#
# First column of the file must contain dates
# First line of the file must contain the headers
#

import readtsv as rt
import writetsv as wt
import energyplot as ep

import numpy as np
import statistics
import matplotlib.pyplot as plt
from decimal import *

plt.autumn()

import pdb

JANELAS = [6,12]

parser = rt.energy_file('example/Carga de Demanda_SIN_03-18.xlsx - Demanda.tsv')
parser.readLines(["NE","N"])
tudo = parser.get_numpy_data()

v = tudo['values'] # Electric Load Value
t = tudo['dates']  # Time YYYYMMDD

def get_numpy_year_month_array(first_year=1970, num_years = 1):
    normalized = []
    for y in range(0,num_years):
        for i in range(1,12):
            dateYDM = str(first_year+y)
            if len(str(i)) < 2:
                dateYDM += "0"
            dateYDM += str(i)
            dateYDM += "01"
            normalized.append(int(dateYDM))
    return np.asarray(normalized)

def get_janela(v, t,anos=10):
    if anos*12 > len(v) or anos*12 > len(t):
        raise Exception("Janela superior à amostra")
    return v[-12*anos:], t[-12*anos:]

def get_deviation(data):
    return statistics.pstdev(data)

def get_variance(data):
    statistics.pvariance(data)

def get_array_max_load_on_the_year(v, t):
    max_v = []
    max_t = []
    max_value = 0
    current_year = int(t[0]/10000)
    for vi, ti in zip(v,t):
        if current_year != int(ti/10000):
            if max_value:
                max_v.append(max_value)
            max_value = 0
            max_t.append(ti)
            current_year = int(ti/10000)
        if vi > max_value:
            max_value = vi

    return np.asarray(max_v), np.asarray(max_t)

def get_array_min_load_on_the_year(v, t):
    min_v = []
    min_t = []
    min_value = float("inf")
    current_year = int(t[0]/10000)
    for ti, vi in zip(t,v):
        if current_year != int(ti/10000):
            if min_value != float("inf"):
                min_v.append(min_value)
            min_value = float("inf")
            min_t.append(ti)
            current_year = int(ti/10000)
        if ti < min_value:
            min_value = vi
    return np.asarray(min_v), np.asarray(min_t)

def get_array_med_load_on_the_year(v, t):
    med_v = []
    med_t = []
    med_value = float("inf")
    current_year = int(t[0]/10000)
    counter = 0
    summ = 0.0
    for ti, vi in zip(t,v):
        if current_year != int(ti/10000):
            med_v.append(summ/counter)
            med_t.append(ti)
            current_year = int(ti/10000)
            counter = 0
            summ = 0.0
        counter += 1
        summ += vi
    return np.asarray(med_v), np.asarray(med_t)


def linear_regression(x, y):
    ''' Receive numpy arrays
        get linear coefficient and constant values
    '''
    sum1 = 0
    sum2 = 0
    ym = y.mean()
    xm = x.mean()

    for xi, yi in zip(x, y):
        sum1 += (xi-xm)*(yi-ym)
        sum2 += (xi-xm) ** 2
    beta = sum1/sum2
    alpha = ym - (beta*xm)

    return alpha,beta

def get_projection(alpha,beta,time):
    projections = np.array([])
    for tx in time:
        proj = alpha + (tx*beta)
        projections = np.append(projections, proj)
    if time[0] == 0:
        pdb.set_trace()
    return time, projections

guesses = {}

#Todo iterar sobre janelas
date_projection = get_numpy_year_month_array(2019,2)

v, t = get_janela(v, t, JANELAS[0])
# alpha,beta = linear_regression(t,v)
# Get median values per month on the years and calculate coefficients
vmed,tmed = get_array_med_load_on_the_year(v,t)
amed, bmed = linear_regression(tmed,vmed)
# Get minimum values per month on the years and calculate coefficients
vmin,tmin = get_array_min_load_on_the_year(v,t)
amin, bmin = linear_regression(tmin,vmin)
# Get maximum values per month on the years and calculate coefficients
vmax,tmax = get_array_max_load_on_the_year(v,t)
amax, bmax = linear_regression(tmax,vmax)

# Run linear projections
#guesses['medio'] = get_projection(alpha, beta, date_projection)
guesses['medio'] = get_projection(amed, bmed, date_projection)
guesses['max'] = get_projection(amax, bmax, date_projection)
guesses['min'] = get_projection(amin, bmin, date_projection)

length = len(guesses['medio'][0])
wt.writetsvdic(guesses, length)
ep.buildgraphic(guesses)
