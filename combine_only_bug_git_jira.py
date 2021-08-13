import xlrd

def read_version_from_xls(file):
    obgjw = xlrd.open_workbook(file)
    obgjs = obgjw.sheets()[0]
    title = obgjs.col_values(0)
    title_flag = False
    res = []
    for i in title:
        if(title_flag == False):
            title_flag = True
            continue
        this_v = i.split('-')[1].split(']')[0]
        res.append(this_v)
        # print(this_v)
    return res

if __name__ == "__main__":
    read_version_from_xls('res/combine2.xls')