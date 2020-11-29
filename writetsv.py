import csv

def writetsv(name, data):
    with open(name+".tsv", 'wt') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        loads = data[1]
        dates = data[0]
        for d,l in zip(dates,loads):
            tsv_writer.writerow([d, l])

def writetsvdic(datas, nlines):
    with open("output/resultado.tsv", 'wt') as out_file:
        # write header
        header = ["Data"]
        for key in datas:
            header.append(key)
        tsv_writer = csv.DictWriter(out_file, delimiter='\t', fieldnames=header)
        tsv_writer.writeheader()

        for i in range(0, nlines):
            tsvlinedic = {}
            for dk in datas.keys():
                tsvlinedic[dk] = datas[dk][1][i]
                tsvlinedic["Data"] = datas[dk][0][i]
            tsv_writer.writerow(tsvlinedic)
