import write_to_xls as wtx
import get_commit_id as gci
import cmd_tool as ct
from time import sleep

def combine_file1_file2(file1,col1,len1,file2,col2,len2,num_loc,max_changed):
    ret = []
    data1 = wtx.get_from_xls(file1,0)
    data2 = wtx.get_from_xls(file2,0)
    ret.append(data1[0]+ data2[0])
    for i in data1[0:]:
        # print(i)
        for j in data2[0:]:
            if(i[col1][0:len1] == j[col2][0:len2] and int(i[num_loc])<=max_changed and int(i[num_loc])>0):
                ret.append(i+j)
    return ret

# 1包含2
def compare_file_single_col(file1,col1,file2,col2):
    data1 = wtx.get_from_xls(file1)
    data2 = wtx.get_from_xls(file2)
    len = 0
    ret = []
    for i in data1:
        if(i[col1] == data2[len][col2]):
            len = len + 1
        else:
            ret.append(i)
    # wtx.save_to_xls([],ret,'1','lost_code')
    return ret

def fix_lost_codes(code_list,nlfile,commit_v,path):
    ct.change_path_to_target(path)
    now_last_list = gci.get_neigh_commit_id(code_list,commit_v)
    this_cid = ''
    this_file = ''
    blame_res = []
    len = 0
    ret = []
    print(now_last_list)
    for i in code_list:
        # print(i)
        if(i[0] != this_cid):
            this_cid = i[0]
            this_file = ''
            print(this_cid)
            ct.run_command('git stash')
            checkout = 'git checkout '+now_last_list.get(this_cid)
            print(checkout)
            ct.run_command(checkout)
            sleep(10)
        if(this_file != i[2]):
            this_file = i[2]
            blame_command = 'git blame -s -f '+this_file
            print(blame_command)
            blame_res = ct.run_command(blame_command)
        for j in blame_res:
            print(j)
            # print(j.split(') ',maxsplit=1)[-1].strip()+" ********* "+i[3])
            if(j.split(') ',maxsplit=1)[-1].strip() == i[3]):
                print(i[3])
                linen = j.split(') ',maxsplit=1)[0]
                # print(j)
                linen = linen.split(' ')[-1]
                sv = j.split(" ")[0][0:8]
                ret.append([i[2],linen,i[3],sv,commit_v.get(sv),
                            now_last_list.get(this_cid),commit_v.get(now_last_list.get(this_cid)),this_cid,commit_v.get(this_cid[0:8])])
                break
    print(ret)
    wtx.save_to_xls([],ret,'temp','3_lost_code_file')
    return ret

def verify_res_file(file1,col1,file2,col2):
    data1 = wtx.get_from_xls(file1)
    data2 = wtx.get_from_xls(file2)
    res = []
    res.append(data1[0][0:1]+data2[0])
    for i in data1[1:]:
        for j in data2[1:]:
            if(i[col1][0:9] == j[col2][0:9]):
                res.append(i[0:1]+j)
    wtx.save_to_xls(res[0],res[1:],'res','4_verify_res_file')

# 嵌套list去重
def remove_same(list):
    b = []
    for i in list:
        if(i not in b):
            b.append(i)
    return b

# file1是git show，file2是获取的lines
def fix_lost_code_main(file1,col1,file2,col2,nl_file,commit_dict,path):
    # res = compare_file_single_col(file1,col1,file2,col2)
    res = compare_res_and_show(file1,file2)
    print(res)
    res = remove_same(res)
    for i in res:
        print(i)
    print(len(res))
    fix_lost_codes(res,nl_file,commit_dict,path)

# file1是获取的lines，file2为git show结果
def compare_res_and_show(file2,file1):
    data1 = wtx.get_from_xls(file1)
    data2 = wtx.get_from_xls(file2)
    ret = []
    for i in data2:
        flag = True
        for j in data1:
            if(i[0] == j[7] and i[3] == j[2] and i[2] == j[0]):
                flag = False
                break
        if(flag):
            ret.append(i)
    return ret