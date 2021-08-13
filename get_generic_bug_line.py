import write_to_xls as wtx
import get_every_version_changedfile as gevc
import get_line_version as glv
import cmd_tool as ct
import os
from time import sleep
import configure as c

res_file_path = c.res_path
headers = ['commit_id','change files','num','version','change num no ann','add_line','del_line']
lines_headers = ['commit_id','change num no ann','version','add_line','del_line']
generic_bug_line_headers = ['file_name','line_number','line','start_commit_id','start_version',
                            'end_commit_id','end_version','delete_commit_id','delete_version']
# git show commitid -U0 filename查看指定文件的添加和删除行
# git show commitid -U0只显示删除添加行

def get_del_add_line(no_anno_list,add_del_lines_file,path,commit_dict):
    ct.change_path_to_target(path)
    ret = []
    for i in no_anno_list:
        file_list = i[1].split('*')[1:]
        this_res = []
        this_res.append(i[0])
        this_res.append(i[3])
        this_res.append(commit_dict.get(i[0]))
        for file in file_list:
            command = 'git show ' + i[0] + " -U0 -- " + file
            res = ct.run_command(command)
            add_line = file
            del_line = file
            for x in res:
                # print(x)
                if(x!='' and (x[0:2] == '- ' or x.startswith('-\t')) and is_annotation(x) == False):
                    del_line = del_line+'*@*'+x
                    # print(x)
                if(x!='' and (x[0:2] == '+ ' or x.startswith('+\t')) and is_annotation(x) == False):
                    add_line = add_line + '*@*' + x
                    # print(x)
            this_res.append(add_line)
            this_res.append(del_line)
        print(this_res)
        ret.append(this_res)
    wtx.save_to_xls(lines_headers,ret,'add_del_lines',add_del_lines_file)
    return ret

# 获取genericbugfixlines，详细见文档
def get_generic_bug_lines(add_del_lines_list,path,res_file,commit_file):
    ret = []
    ct.change_path_to_target(path)
    # commit_v = glv.get_commit_id(commit_file,8,False)
    commit_v = glv.get_commit_id(commit_file,8)
    keys = list(commit_v.keys())
    for i in add_del_lines_list:
        print(i[0])
        v = commit_v.get(i[0][0:8])
        print(commit_v)
        end_version = keys[v+1]
        print("now_V:"+i[0] + " end_v:"+ end_version)
        check_out_command = "git checkout "+end_version
        print(check_out_command)
        ct.run_command('git stash')
        ct.run_command(check_out_command)
        sleep(10)
        for num in range(0,int(i[1])):
            col = i[4+num*2]
            file_and_del = col.split('*@*')
            blame_command = 'git blame -s -f '+file_and_del[0]
            print(blame_command)
            cmd_blame_res = ct.run_command(blame_command)
            cid_code = get_version_code(cmd_blame_res)
            # print(cid_code)
            ret = ret + get_start_v_list(cid_code,file_and_del[1:],end_version,file_and_del[0],commit_v,i[0],v)
    wtx.save_to_xls(generic_bug_line_headers,ret,'generic_bug_lines',res_file)
    return ret

def get_start_v_list(blame_lines,fix_lines,end_v,file_name,commit_v,now_cid,now_v):
    ret = []
    counter = 0
    for i in fix_lines:
        while(counter < len(blame_lines)):
            j = blame_lines[counter]
            counter = counter + 1
            # print(str(counter)+"---"+j[1]+"------"+i[1:].strip())
            if(len(j[1].split('*@*'))>1):
                j[1] = j[1].split('*@*')[0]
            if(j[1] == i[1:].strip()):
                # print(end_v)
                # print(j[0])
                ret.append([file_name,j[2],j[1],j[0],commit_v.get(j[0])+1,end_v,commit_v.get(end_v)+1,now_cid,now_v+1])
                break
    print(ret)
    return ret

def get_version_code(blame_res,c_len=8):
    ret = []
    for i in blame_res:
        # print(i)
        if(len(i)> 8 and i[0] == '^'):
            commit_id = i[1:c_len+1]
        else:
            commit_id = i[0:c_len]
        code = i.split(')',maxsplit=1)[-1].strip()
        line_number = i.split(')',maxsplit=1)[0]
        line_number = line_number.split(' ')[-1]
        ret.append([commit_id,code,line_number])
    return ret

def split_show_to_every_lines(file,res_file_name):
    header = ['commit id','version','file','code']
    file = res_file_path + "res/" + file + ".xls"
    combine_lines =  wtx.get_from_xls(file)
    ret = []
    for line in combine_lines:
        for i in range(0,int(line[1])):
            col = line[4+i*2]
            code_line = col.split('*@*')
            for code in code_line[1:]:
                this_res = [line[0],line[2],code_line[0],code[1:].strip()]
                # print(code[1:].strip())
                # print(this_res)
                ret.append(this_res)
    wtx.save_to_xls(header,ret,'all line',res_file_name)
    return ret

# 嵌套list去重
def remove_same(list):
    b = []
    for i in list:
        if(i not in b):
            b.append(i)
    return b

def from_combine_to_only_bug_version(file):
    file_data = wtx.get_from_xls(file,0)
    ret = []
    for i in file_data:
        if(i[7] == 'Bug' and (i[8] == 'Resolved' or i[8] == 'Closed')):
            ret.append(i)
    wtx.save_to_xls(file_data[0],ret,'only bug version','1_get_only_bug_version')
    return ret

def is_annotation(str):
    return len(str.split(' //'))>1 or len(str.split('// '))>1 or len(str.split(' *'))>1 or len(str.split('* '))>1

