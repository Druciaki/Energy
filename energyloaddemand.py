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
from scipy.optimize import least_squares
from scipy.optimize import curve_fit
import scipy

from decimal import *
import pdb

plt.autumn()

JANELAS = [6,12]
PREVISAO_ANO = 2

#2013 - 2018
parser = rt.energy_file('example/Carga de Demanda_SIN_03-18.xlsx - Demanda.tsv')
parser.readLines(["NE","N"])
tudo = parser.get_numpy_data()

#2019 - out 2020
read = rt.energy_file('example/1920.load.tsv')
read.readLines(["NE","N"])
tudo2 = read.get_numpy_data()

def mape(y_true, y_pred): 
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def readable_date(date): # Receive YYYYMMDD and return readable date
    sdate = str(date)
    return sdate[6:8]+"/"+sdate[4:6]+"/"+sdate[0:4]

def get_numpy_year_month_array(first_year=1970, num_years = 1):
    normalized = []
    for y in range(0,num_years):
        for i in range(1,13):
            dateYDM = str(first_year+y)
            if len(str(i)) < 2:
                dateYDM += "0"
            dateYDM += str(i)
            dateYDM += "01"
            normalized.append(int(dateYDM))
    return np.asarray(normalized)

def get_janela(v, t, anos=10):
    if anos*12 > len(v) or anos*12 > len(t):
        raise Exception("Janela superior à amostra")
    return v[-12*anos:], t[-12*anos:]

def get_deviation(data):
    return statistics.pstdev(data)

def get_variance(data):
    statistics.pvariance(data)

def get_projection(alpha,beta,time):
    projections = np.array([])
    for tx in time:
        proj = alpha + (tx*beta)
        projections = np.append(projections, proj)
    return time, projections

def neutral_value(alpha, beta, time):
    return alpha+beta*time

def neutral_func(x, alpha, beta):
    return alpha+beta*x

def pessimistic_value(alpha, beta, time):
    return alpha*np.exp(beta*time)

def pessimistic_func(x, alpha, beta):
    return alpha*np.exp(beta*x)

def otimistic_value(alpha, beta, time):
    return alpha*np.log(beta*time)

def otimistic_func(x, alpha, beta):
    return alpha*np.log(beta*x)

def get_projection(a, b, func, time):
    projection = []
    for t in time:
        projection.append(func(t,a,b))
    return np.asarray(projection)

#### INIT ####
for janela in JANELAS:
    # v = tudo['values'] # Electric Load Value
    # t = tudo['dates']  # Time YYYYMMDD
    v, t = get_janela(tudo['values'], tudo['dates'], janela)

    ts = np.arange(0, len(t))
    ts += 1

    ### Iniciando os calculos ###

    # Encontrando constantes das funções de projeção
    ap, bp = scipy.optimize.curve_fit(pessimistic_func,ts,v,p0=(10000,0))[0]
    ao, bo = scipy.optimize.curve_fit(otimistic_func,ts,v)[0]
    an, bn = scipy.optimize.curve_fit(neutral_func,ts,v)[0]

    # Projetando os valores sobre as equações encontradas
    pes = get_projection(ap, bp, pessimistic_func, ts)
    oti = get_projection(ao, bo, otimistic_func, ts)
    neu = get_projection(an, bn, neutral_func, ts)

    # Calculando Erro percentual médio de cada solução
    mape_otimista = mape(v, oti)
    mape_pessimista = mape(v, pes)
    mape_neutro = mape(v, neu)


    plt.clf()
    plt.plot(ts, v, 'o', label="Amostras")
    plt.plot(ts, oti, '-', label="Otimista")
    plt.plot(ts, pes, '-', label="Pessimista")
    plt.plot(ts, pes, '-', label="Neutro")
    plt.legend()
    plt.xlabel("Tempo (em meses) de "+readable_date(t[0])+" a "+readable_date(t[-1]))
    plt.ylabel("Carga")
    plt.savefig("output/geral"+str(janela)+".png")

    results = {'Data':[readable_date(tr) for tr in t],
               'N.Mes':ts,
               'Leitura':v,
               'Neutro':neu,
               'Pessimista':pes,
               'Otimista':oti}

    wt.writetsvdic(results, len(ts), "output/proj"+str(janela)+".tsv")
    report = open("output/report"+str(janela)+".txt", 'wt')
    report.write("Análise até 2018\n")
    report.write("Abordagem Neutra\tMAPE:"+str(mape_neutro)+"\tY(t)="+str(an)+"+ t*"+str(bn)+"\n")
    report.write("Abordagem Pessimista\tMAPE:"+str(mape_pessimista)+"\tY(t)="+str(ap)+"*e^("+str(bp)+"*t)\n")
    report.write("Abordagem Otimista\tMAPE:"+str(mape_otimista)+"\tY(t)="+str(ao)+"*ln("+str(bo)+"*t)\n")
    #report.close()


    # Aux data for "future" projections on 2019 and 2020
    date_projection = get_numpy_year_month_array(2019,2)
    ts2 = np.asarray([i for i in range(ts[-1],ts[-1]+len(date_projection))])
    # Projetando os valores sobre as equações encontradas
    pes = get_projection(ap, bp, pessimistic_func, ts2)
    oti = get_projection(ao, bo, otimistic_func, ts2)
    neu = get_projection(an, bn, neutral_func, ts2)
    v, t = tudo2['values'], tudo2['dates']

    tsplot = ts2 - ts2[0]
    plt.clf()
    plt.plot(tsplot[:-(len(ts2)-len(t))], v, 'o', label="Amostras")
    plt.plot(tsplot, oti, '-', label="Otimista")
    plt.plot(tsplot, pes, '-', label="Pessimista")
    plt.plot(tsplot, pes, '-', label="Neutro")
    plt.legend()
    plt.xlabel("Tempo (em meses) de "+readable_date(t[0])+" a "+readable_date(t[-1]))
    plt.ylabel("Carga")
    plt.savefig("output/geral1920"+str(janela)+".png")

    report.write("\n\nAnálise 2019 - 2020\n")
    mape_otimista =   mape(v, oti[:len(v)])
    mape_pessimista = mape(v, pes[:len(v)])
    mape_neutro =     mape(v, neu[:len(v)])
    report.write("Abordagem Neutra\tMAPE:"+str(mape_neutro)+"\tY(t)="+str(an)+"+ t*"+str(bn)+"\n")
    report.write("Abordagem Pessimista\tMAPE:"+str(mape_pessimista)+"\tY(t)="+str(ap)+"*e^("+str(bp)+"*t)\n")
    report.write("Abordagem Otimista\tMAPE:"+str(mape_otimista)+"\tY(t)="+str(ao)+"*ln("+str(bo)+"*t)\n")
    report.close()

    # Projetar melhor solução até dezembro de 2023
