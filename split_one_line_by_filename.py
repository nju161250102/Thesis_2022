import write_to_xls as wtx

headers = ['commit id','file','add line num','del line num']

def split_one_line_by_filename(filaname):
    res = wtx.get_from_xls(filename)
    ret = []
    for i in res:
        this_res = [i[0],'','','']
        for n in range(int(i[1])):
            this_res[1] = i[3+n*2].split('*@*')[0]
            this_res[2] = len(i[3+n*2].split('*@*'))-1
            this_res[3] = len(i[4+n*2].split('*@*'))-1
            print(this_res)
            ret.append(this_res)
    wtx.save_to_xls(headers,ret,'res','2_one_line_one_file')

if __name__ == "__main__":
    filename = 'res/2_add_del_lines_NoAnno_and_less4.xls'
    split_one_line_by_filename(filename)