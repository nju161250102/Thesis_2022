import os
import xlrd
import write_to_xls as wtx
import re
import subprocess
import get_every_version_changedfile as gevc
import combine_only_bug_git_jira as cobgj
import configure as c

headers = ['commit_id','file','line','code','version']

# 获取所有行的版本信息
def get_file_version(commit_id,path):
    change_path()
    # commendline = 'git blame '+path
    commendline = 'git blame -s -f '+path #不显示作者和时间戳
    # print(os.getcwd())
    # os.system(commendline)
    print(commendline)
    res = os.popen(commendline)
    res = res.buffer.read().decode(encoding='utf-8').split('\n')
    res.pop()
    ret = []
    res_map = {}
    for i in res:
        version = commit_id.get(i[0:10])
        # print(str(version)+" " +i)
        this_ret = re.split(r'[ ]+',i,maxsplit=3)
        res_map.update({this_ret[3]:version})
        this_ret.append(version)
        ret.append(this_ret)
    return ret,res_map

# 获取当前版本改动行
def get_now_file_version(commit_id,path,v):
    change_path()
    # commendline = 'git blame '+path
    commendline = 'git blame -s -f '+path #不显示作者和时间戳
    # os.system(commendline)
    print(commendline)
    res = os.popen(commendline)
    res = res.buffer.read().decode(encoding = 'utf-8').split('\n').pop()
    ret = []
    res_map = {}
    for i in res:
        version = commit_id.get(i[0:10])
        # print(str(version)+" " +i)
        this_ret = re.split(r'[ ]+',i,maxsplit=3)
        if i[0:10] == v:
            res_map.update({this_ret[3]:version})
        this_ret.append(version)
        ret.append(this_ret)
    return ret,res_map

# file内容是需要检测的java文件名称
def get_all_file_version(commit_id,file):
    f = open(file,'r',encoding='utf-8')
    v = get_this_version()
    print(commit_id.get(v))
    for i in f:
        ret,ret_map = get_file_version(commit_id,i)
        # ret,ret_map = get_now_file_version(commit_id,i,v)
        print(ret_map)

# 检测指定dict内的文件的版本信息
def get_all_file_versionbydict(commit_id,dict):
    v = get_this_version()
    print(v)
    # print(dict)
    file_list = dict[v[0:9]]
    for i in file_list:
        ret,ret_map = get_file_version(commit_id,i)
        print(ret_map)

# 读取commit id并按照顺序映射到dict中
def get_commit_id(file,len = 10,containMerge = True):
    res = {}
    # comw = xlrd.open_workbook(file)
    # coms = comw.sheets()[0]
    # comt = coms.col_values(0)
    comt = wtx.get_from_xls(file)
    line = 0
    for i in comt :
        if(i[1] == '' and containMerge == False):
            continue
        res.update({i[0].split('\n')[0][:len]:line})
        line = line + 1
    # print(res)
    return res

# 获取当前版本的commit id
def get_this_version():
    change_path()
    commend_line = 'git rev-parse HEAD'
    res = os.popen(commend_line).readlines()
    return res[0][0:10]

# 获取generic_bug_fix_version
def get_bugfix_version(commit_id,lens=10):
    bugfix_file = c.res_path+"res/combine2.xls"
    keys = []
    values = []
    for key,value in commit_id.items():
        keys.append(key)
        values.append(value)
    # print(keys)
    # print(values)
    only_bug = {}
    only_bug_version = cobgj.read_version_from_xls(bugfix_file)
    for i in only_bug_version:
        git_id = keys[values.index(int(i))]
        only_bug.update({git_id[0:lens]:i})
        # print(i + " "+ git_id)
    return only_bug

def get_change_more_4_and_fix_version(file_name,commit_id):
    git_version_dict = get_bugfix_version(commit_id)
    # print(git_version_dict)

    workbook = xlrd.open_workbook(file_name)
    sheet = workbook.sheets()[0]
    title = sheet.col_values(0)
    change_num = sheet.col_values(2)
    # print(title)
    # print(change_num)
    ret = {}
    for i in range(1,len(title)):
        num = change_num[i].strip()
        version = git_version_dict.get(title[i][0:10])
        if(is_number(num) or version == None):
            continue
        # print('num:' + num)
        if(int(num)<=4):
            ret.update({title[i][0:9]:version})
    return ret

def is_number(s):
    try:
        float(s)
        return False
    except ValueError:
        return True

if __name__ == "__main__":
    file_name = 'res/log.xls'
    commit_id  = get_commit_id('res/combine1.xls')
    ret = get_change_more_4_and_fix_version(file_name,commit_id)
    print(ret)
    print(len(ret))
    # if(is_number(' ')):
    #     print('yes')
    # ob = get_bugfix_version()
    # print(ob)

    # commit_id = get_commit_id('res/combine1.xls')
    # print(commit_id)
    # get_all_file_version(commit_id,'res/all_diff_test.txt')

    # path = 'E:\\projects\\git\\mooctest\\tika-1\\'
    # ret = gevc.get_every_version_changedfile(path)
    # get_all_file_versionbydict(commit_id,ret)