
from openpyxl import load_workbook

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def loadExcel(fname, sheet:str, top:tuple, bottom:tuple, flip:bool=False):
    wb = load_workbook(filename = fname)
    ws = wb[sheet]

    if bottom[1] == -1:
        bottom = [bottom[0],ws.max_row]

    data = []
    for i in range(top[1], bottom[1]+1):
        data.append([])

        for j in range(top[0], bottom[0]+1):
            data[-1].append(ws.cell(row=i, column=j).value)

    if flip:
        data = [[data[i][j] for i in range(len(data))] for j in range(len(data[0]))]

    return data
    
