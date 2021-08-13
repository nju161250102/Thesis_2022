import from_gitlog_get_info as fggi
import from_web_get_jira_Data as fwgjd
import combine_jira_gitlog as cjg
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
import configure as c
import main_func as mf

def get_data():
    if(os.path.exists(c.res_path+'init_data') == False):
        os.mkdir(c.res_path+'init_data')
    if(os.path.exists(c.res_path+'res') == False):
        os.mkdir(c.res_path+'res')
    # fggi.get_log_info()
    # fwgjd.get_jira_info()
    # cjg.combine_git_jira()
    # mf.main_func()

if __name__ == "__main__":
    get_data()