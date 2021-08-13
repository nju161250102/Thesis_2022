import os
import cmd_tool
import sys
import write_to_xls as wtx
import get_line_version as glv
import configure as c

headers = ['commit_id','change files','num','version']

def get_every_version_changedfile(path):
    commend_line = 'git log --name-only --oneline'
    cmd_tool.change_path_to_target(path)
    com_res = os.popen(commend_line)
    com_res = com_res.buffer.read().decode(encoding = 'utf-8')
    ret = {}
    res = []
    version = ''
    flag = False
    for i in com_res.split('\n'):
        # print(i)
        if(len(i.split()) == 1):
            res.append(i)
        elif(flag):
            ret.update({version:res})
            # print(version)
            # print(res)
            version = i.split(' ')[0]
            res = []
        else:
            version = i.split(' ')[0]
            flag = True
    return ret

def get_every_version_changedjavafile(path):
    commend_line = 'git log --name-only --oneline'
    cmd_tool.change_path_to_target(path)
    com_res = os.popen(commend_line)
    com_res = com_res.buffer.read().decode(encoding = 'utf-8')
    ret = []
    version = ''
    this_res = []
    res = ""
    for i in com_res.split('\n'):
        # print(i)
        if(len(i.split())>1):
            numl = len(res.split('*'))-1
            if(numl<=4 and numl > 0):
                this_res.append(res)
                this_res.append(numl)
                ret.append(this_res)
            this_res = []
            res = ""
            index = i.split()
            this_res.append(index[0])
        elif(len(i.split()) == 1):
            if(i[-5:] == '.java'):
                res = i + '*' + res
    # del(ret[0])
    return ret

def save_cid_version(path,commit_file):
    res = get_every_version_changedjavafile(path)
    commit_id = glv.get_commit_id(commit_file)
    commit_id  = glv.get_bugfix_version(commit_id,9)
    # print(commit_id.get('5e2a3c081'))
    ret = []
    for i in res:
        if(commit_id.get(i[0])!= None):
            i.append(commit_id.get(i[0]))
            ret.append(i)
    print(commit_id)
    print(res)
    print(ret)
    wtx.save_to_xls(headers,ret,'onlu_java_changed','only_java_changed_numlessthan4_and_bugfixversion')
    return ret

if __name__ == "__main__":
    commit_file = c.res_path + 'res/combine1.xls'
    path = 'E:\\projects\\git\\mooctest\\tika-1\\'
    # res = get_every_version_changedfile(path)
    save_cid_version(path,commit_file)
    # wtx.save_to_xls(headers,res,'only_java_changed_file','only_java_changed_num')
    # print (res)
    # print(res['5e2a3c081'])