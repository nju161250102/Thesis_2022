import cmd_tool as ct
import write_to_xls as wtx

def filter_not_bug_version(file_data):
    ret = []
    for i in file_data:
        if(i[7] == 'Bug' and (i[8] == 'Resolved' or i[8] == 'Closed')):
            ret.append(i)
    # wtx.save_to_xls(file_data[0],ret,'only bug version','1_get_only_bug_version')
    return ret

def filter_more_than_n_version(first_commit_id,file_data,path,only_java=True,max_num = 4):
    ret = []
    data_ret = []
    this_res = []
    res = ""
    ct.change_path_to_target(path)
    c1 = 'git config --global merge.renameLimit 99999'
    ct.run_command(c1)
    commend_line = 'git log --name-only --oneline '+first_commit_id.strip()
    print(commend_line)
    cmd_res = ct.run_command(commend_line)
    for i in cmd_res:
        if (len(i.split(' ')) > 1):
            numl = len(res.split('*')) - 1
            if (numl <= max_num and numl>0):
                print(this_res[0])
                this_res.append(res)
                this_res.append(numl)
                this_data = exist_data(file_data,this_res[0][0:8],8)
                if(this_data!= []):
                    ret.append(this_res)
                    data_ret.append(this_data)
            this_res = []
            res = ""
            index = i.split()
            this_res.append(index[0])
        elif (len(i.split()) == 1):
            if (only_java != True or (i[-5:] == '.java' and i[-9:-5]!='Test')):
                res = i + '*' + res
    return ret,data_ret

def filter_annotation(cid_file_list, path):
        ct.change_path_to_target(path)
        ret = []
        for i in cid_file_list:
            file_list = i[1].split('*')
            del (file_list[-1])
            # print(file_list)
            changed_num = 0
            flag = 0
            add_line = ''
            del_line = ''
            change_file = ''
            for j in file_list:
                command = 'git show ' + i[0] + " -U0 -- " + j
                print(command)
                res = ct.run_command(command)
                # print(command)
                for x in res:
                    # print(x)
                    if (x != '' and ((x[0] == '-' and len(x)>1 and x[1]!='-') or x.startswith('-\t')) and is_annotation(x) == False):
                        flag = 1
                        del_line = del_line + '*@*' + x
                        # print(x)
                    if (x != '' and ((x[0] == '+' and len(x)>1 and x[1]!='+') or x.startswith('+\t')) and is_annotation(x) == False):
                        flag = 1
                        add_line = add_line + '*@*' + x
                        # print(x)
                if (flag == 1):
                    changed_num = changed_num + 1
                    if (changed_num < 10):
                        change_file = change_file + '*' + j
            if (changed_num != i[2]):
                print(str(changed_num) + " " + str(i[2]) + " " + i[0])
            this_res = i
            this_res[1] = change_file
            this_res.append(changed_num)
            # this_res.append(add_line)
            # this_res.append(del_line)
            ret.append(this_res)
        # print('yes')
        return ret

def is_annotation(str):
    return len(str.split(' //'))>1 or len(str.split('// '))>1 \
           or len(str.split(' *'))>1 or len(str.split('* '))>1 \
           or len(str.split('/*'))>1 or len(str.split('*/'))>1

def exist_data(data,commit_id,len = 8):
    for i in data:
        if(commit_id == i[0][0:len]):
            return i
    return []