import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
import write_to_xls as wtx
import configure as c
import cmd_tool as ct

headers = ['commit_id','date','change file','add lines num','del lines num','title']
pro_name = c.pro_name

# git log --before='2021.06.30'  获得之前的版本
# git log --stat 获得修改文件信息

def get_data(path):
    ct.change_path_to_target(path)
    cmd_res = ct.run_command('git log --stat --before=\'2021.06.30\'')
    res = []
    i = 1
    this_res = []
    title = ''
    for i in cmd_res:
        if(i[0:6] == 'commit'):
            if(len(this_res)<4):
                this_res.append('')
                this_res.append('')
                this_res.append('')
            this_res.append(title)
            title = ''
            res.append(this_res)
            this_res = []
            this_res.append(i.split(' ')[1].strip())
        elif(i[0:6] == 'Date: '):
            this_res.append(i.split(':   ')[1].strip())
        elif(i[0:4]=='    '):
            title = title+i
        elif(' changed, ' in i):
            this_res.append(i.split('file')[0].strip())
            temp = i.split('changed, ')[-1].split(' insertions')[0]
            if (len(temp) > 3):
                this_res.append('0')
            else:
                this_res.append(temp)
            temp = i.split('(+), ')[-1].split(' deletions(-)')[0]
            if (len(temp) > 3):
                this_res.append('0')
            else:
                this_res.append(temp)
        print(i)
    res.append(this_res)
    print(res[1:])
    print(len(res))
    return res[1:]

def get_log_info():
    path = c.path
    res = get_data(path)
    wtx.save_to_init_xls(headers,res,pro_name,'git_log_info')
    wtx.save_to_xls(headers,res,pro_name,'combine1')

if __name__ == "__main__":
    get_log_info()