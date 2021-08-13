import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
import write_to_xls as wtx
import configure as c
import re

pro_name = c.jira_name
project_init_data_path = "E:/projects/py/numpytest/test/venv/Include/find_bug_lines/init_data/"

def combine_gitlog_jira(filepath1,filepath2):
    filedata = wtx.get_from_xls(filepath1,0)
    bug_dict,title2 = get_bug_version_dict(filepath2)
    # print(bug_dict)
    ret = []
    headers = filedata[0]+title2
    for i in filedata[1:]:
        pat = re.compile(r''+pro_name+'-\d+')
        thisvs = pat.findall(i[5])
        for j in thisvs:
            thisv = j.split(pro_name+'-')[1]
            # print(thisv)
            jira_data = bug_dict.get(int(thisv))
            if(jira_data != None):
                ret.append(i + bug_dict.get(int(thisv)))
    wtx.save_to_xls(headers,ret,'all_info','1_get_only_bug_version_all_match')
    return ret

def combine_gitlog_jira_once(filepath1,filepath2):
    filedata = wtx.get_from_xls(filepath1,0)
    bug_dict,title2 = get_bug_version_dict(filepath2)
    # print(bug_dict)
    ret = []
    headers = filedata[0]+title2
    for i in filedata[1:]:
        pat = re.compile(r''+pro_name+'-\d+')
        thisvs = pat.findall(i[5])
        for j in thisvs:
            thisv = j.split(pro_name+'-')[1]
            # print(thisv)
            jira_data = bug_dict.get(int(thisv))
            if(jira_data != None):
                ret.append(i + bug_dict.get(int(thisv)))
            break
    wtx.save_to_xls(headers,ret,'all_info','1_get_only_bug_version')
    return ret

def get_bug_version_dict(file_path):
    data = wtx.get_from_xls(file_path,0)
    res_dict = {}
    for i in data[1:]:
        v = int(i[0].split('-',maxsplit=1)[1].split(']')[0])
        res_dict.update({v:i})
    return res_dict,data[0]

def combine_git_jira():
    filename1 = 'git_log_info'
    filepath1 = project_init_data_path+filename1+'.xls'
    filename2 = 'jira_issue_info_only_bug_version'
    filepath2 = project_init_data_path+filename2+'.xls'
    combine_gitlog_jira(filepath1,filepath2)
    combine_gitlog_jira_once(filepath1,filepath2)

if __name__ == '__main__':
    combine_git_jira()
    # s = '    IVY-1586 IVY-1610 Make sure that empty value of "classifier" in pom.xml is considered the same as classifier not being specified'
    # print(s.split('IVY-')[1:])
