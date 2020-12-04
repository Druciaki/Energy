import matplotlib.pyplot as plt
from decimal import *

def buildgraphic(guesses,outputfile="output/CargaEletrica.png"):
    plt.clf()
    for name in guesses:
        data = guesses[name]
        x ,y = None, None # Hotfix - assure parameter type (TODO:REVIEW)
        if type(data[0]) != type(list()):
            x = data[0].tolist()
        else:
            x = data[0]
        if type(data[1]) != type(list()):
            y = data[1].tolist()
        else:
            y = data[1]

        for i in range(0, len(data[0])):
            x[i] = Decimal(data[0][i]/1000000)

        plt.plot(x, y, label=name)


    plt.xlabel('Tempo')
    plt.ylabel('Carga')
    plt.title('Previsao via Regressao Linear')
    plt.legend()
    plt.savefig(outputfile) 
    #plt.show()

