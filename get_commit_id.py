import write_to_xls as wtx

def get_commit_id(file,len = 10,containMerge = True):
    res = {}
    # comw = xlrd.open_workbook(file)
    # coms = comw.sheets()[0]
    # comt = coms.col_values(0)
    comt = wtx.get_from_xls(file)
    line = 0
    for i in comt :
        line = line + 1
        if(i[1] == '' and containMerge == False):
            continue
        res.update({i[0].split('\n')[0][:len]:line})
    # print(res)
    return res

def get_neigh_commit_id_and_save(add_del_lines_list,file_path,res_file_name):
    commit_v = get_commit_id(file_path,8,False)
    print(commit_v)
    keys = list(commit_v.keys())
    res = []
    ret = {}
    for i in add_del_lines_list:
        v = commit_v.get(i[0][0:8])
        print(v)
        end_version = keys[v]
        res.append([v,i[0],end_version])
        ret.update({i[0]:end_version})
    if(res_file_name != ''):
        wtx.save_to_xls(['v','now','last'],res,'res',res_file_name)
    return ret

def get_neigh_commit_id(add_del_lines_list,commit_v):
    keys = list(commit_v.keys())
    ret = {}
    print(len(keys))
    for i in add_del_lines_list:
        v = commit_v.get(i[0][0:8])
        # print(v)
        # end_version = keys[keys.index(v)+1]
        end_version = keys[v]
        ret.update({i[0]:end_version})
    return ret