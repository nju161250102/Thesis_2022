import os
from time import sleep

import pandas as pd
from copy import deepcopy
from threading import Thread

from flask import Flask, render_template, session, request, redirect
from flask.logging import default_handler
from Logger import LOG

from active import ActiveLearningModel
from data import ReportData
from model import Alarm
from service import WorkerService, ProjectService, AlarmService, LabelService
from utils import CommandUtils, PathUtils
from ExtractFeature import extract_one_version


app = Flask(__name__)
app.secret_key = os.urandom(16)
app.logger.removeHandler(default_handler)
app.logger.addHandler(LOG.handlers[0])

# 管理员界面标题栏
admin_nav_list = [{
    "name": "所有项目",
    "active": False,
    "url": "/"
}, {
    "name": "项目上传",
    "active": False,
    "url": "/upload"
}, {
    "name": "查看报告",
    "active": False,
    "url": "/report"
}]
# 工人界面标题栏
worker_nav_list = [{
    "name": "审核任务",
    "active": False,
    "url": "/"
}, {
    "name": "审核历史",
    "active": False,
    "url": "/history"
}]


def merge_alarm(alarm_id: str) -> dict:
    """
    合并警告的项目信息和审核标记
    :param alarm_id: 警告ID
    """
    alarm = AlarmService.get_by_id(alarm_id)
    project = ProjectService.get_by_id(alarm["project_id"])
    label = LabelService.get_by_alarm(alarm_id)
    alarm["name"] = project["name"]
    alarm["version"] = project["version"]
    alarm["label"] = label["value"]
    alarm["label_time"] = label["label_time"]
    return alarm


def login_auth(func):
    """
    身份验证装饰器
    :param func: 被包装的函数
    """
    def inner(*args, **kwargs):
        if session.get("username") is None:
            # session["id"] = -1
            # session["username"] = "admin"
            # session["userType"] = "admin"
            # return func(*args, **kwargs)
            return redirect("/login")
        else:
            return func(*args, **kwargs)
    return inner


def project_thread(name: str, version: str, project_id: int):
    # 解压文件
    CommandUtils.run("unzip -o -q -d {0} {1}".format(PathUtils.project_path(name, version),
                                                  PathUtils.project_path(name, version + ".zip")))
    # 漏洞扫描
    PathUtils.rebuild_dir(PathUtils.report_path(name), skip=True)
    CommandUtils.run_spotbugs(PathUtils.project_path(name, version + ".jar"),
                              PathUtils.report_path(name, version + ".xml"))
    # 读取警告
    alarm_list = ReportData.read_report(name, version)[:20]
    alarm_df = pd.DataFrame([alarm.__dict__ for alarm in alarm_list])
    # 代码行变更
    alarm_df = ReportData.update_alarm(alarm_df, name)
    # 更新new_location
    alarm_list = Alarm.from_dataframe(alarm_df)
    # 保存警告
    alarm_id_list = [AlarmService.save(alarm, project_id) for alarm in alarm_list]
    # 提取特征
    feature_df = extract_one_version(alarm_df, name, version)
    # 保存特征
    # feature_df.to_csv(PathUtils.feature_path(name + ".csv"))
    ProjectService.change_state(project_id, 1)
    # 调用主动学习模型
    model_config = {
        "init_sample": {
            "name": "random",
            "sample_num": 5,
            "stop_threshold": 1,
            "cluster_n": 5
        },
        "learn_model": {
            "name": "bagging"
        },
        "query_strategy": {
            "name": "certain_query",
            "max_num": 5
        },
        "stop_strategy": {
            "name": "never"
        }
    }

    def ask_label(index_set: set):
        # 分配给工人标记
        LabelService.add_labels(index_set)
        # 每隔一段时间检查是否全部审核过
        while not LabelService.check_all_labeled(index_set):
            sleep(30)

    active_learner = ActiveLearningModel(config=model_config, query_func=ask_label)
    active_learner.run(feature_df, metric_flag=False)
    ProjectService.change_state(project_id, 2)


@app.route("/", methods=["GET", "POST"])
def main_page():
    # 判断是否登录覆盖
    if "username" not in session:
        username = request.form.get("username")
        password = request.form.get("password")
        # 非登录请求跳转到登录页面
        if username is None or password is None:
            return redirect("/login")
        # 密码校验
        user_id = WorkerService.login(username, password)
        if user_id != -2:
            session["id"] = user_id
            session["username"] = username
            session["userType"] = "admin" if username == "admin" else "worker"
        else:
            return render_template("login.html", info="用户名或密码错误")
    # 此时session中已有username字段，根据用户类型返回页面
    page = request.args.get("page", 1, type=int)
    if session["userType"] == "admin":
        state_dict = {
            "all": -1,
            "scan": 0,
            "check": 1,
            "done": 2
        }
        # 根据状态值筛选
        state_str = request.args.get("type", "all", type=str)
        page_sum = ProjectService.page_count(state_dict[state_str])
        # 获取项目列表
        project_list = ProjectService.get_list(state_dict[state_str], page)
        index_nav_list = deepcopy(admin_nav_list)
        index_nav_list[0]["active"] = True
        return render_template("admin_index.html", title="首页", nav_list=index_nav_list, username=session["username"],
                               project_list=project_list, state=state_str, page_config=get_page_config(page, page_sum))
    else:
        page_sum = LabelService.page_count_my_alarms(session["id"], False)
        alarm_id_list = LabelService.get_my_alarms(session["id"], False, page)
        alarm_list = [merge_alarm(alarm_id) for alarm_id in alarm_id_list]
        index_nav_list = deepcopy(worker_nav_list)
        index_nav_list[0]["active"] = True
        return render_template("worker_index.html", title="首页", nav_list=index_nav_list, username=session["username"],
                               alarm_list=alarm_list, page_config=get_page_config(page, page_sum))


@app.route("/upload", methods=["GET", "POST"], endpoint="upload")
@login_auth
def upload_page():
    # 记录返回的提示信息
    info = None
    # 如果是上传请求
    if request.method == "POST":
        # 省略了对参数重复性的校验
        try:
            # 接收参数
            name = request.form.get("name")
            version = request.form.get("version")
            description = request.form.get("description")
            zip_file = request.files.get("zip")
            jar_file = request.files.get("jar")
            # 文件夹不存在时创建
            project_dir = PathUtils.project_path(name)
            PathUtils.rebuild_dir(project_dir, skip=True)
            # 保存文件
            zip_file.save(PathUtils.project_path(name, version + ".zip"))
            jar_file.save(PathUtils.project_path(name, version + ".jar"))
            # 保存到数据库
            project_id = ProjectService.save(name=name, version=version, description=description)
            # 启动线程
            t = Thread(target=project_thread, name="Project-" + name, args=(name, version, project_id))
            t.start()
            info = "项目上传成功"
        except Exception:
            info = "上传项目时出错"

    upload_nav_list = deepcopy(admin_nav_list)
    upload_nav_list[1]["active"] = True
    return render_template("admin_upload.html", title="项目上传", nav_list=upload_nav_list, username=session["username"],
                           info=info)


@app.route("/report", methods=["GET"], endpoint="report")
@login_auth
def report_page():
    # 获得审核完毕的项目列表
    project_list = ProjectService.get_list(state=2)
    alarm_list = None
    page_config = None
    project_id = request.args.get("project", None)
    if project_id:
        # 获取项目下的警告列表
        page = request.args.get("page", 1, type=int)
        page_sum = AlarmService.page_count_by_project(project_id)
        page_config = get_page_config(page, page_sum)
        alarm_id_list = AlarmService.get_by_project(project_id, page)
        alarm_list = [merge_alarm(alarm_id) for alarm_id in alarm_id_list]
    report_nav_list = deepcopy(admin_nav_list)
    report_nav_list[2]["active"] = True
    return render_template("admin_report.html", title="查看报告", nav_list=report_nav_list, username=session["username"],
                           project_list=project_list, alarm_list=alarm_list, page_config=page_config, project_id=project_id)


@app.route("/detail/<int:alarm_id>", methods=["GET", "POST"], endpoint="detail")
@login_auth
def detail_page(alarm_id):
    info = None
    if request.method == "POST":
        label_str = request.form.get("result")
        if label_str is None:
            info = "请选择标记结果"
        else:
            LabelService.update_label(alarm_id, 1 if label_str == "yes" else 0)
            return redirect("/")
    alarm = merge_alarm(alarm_id)
    code = AlarmService.get_code(alarm_id)
    return render_template("worker_detail.html", title="漏洞详情", nav_list=worker_nav_list, username=session["username"],
                           alarm=alarm, code=code, info=info)


@app.route("/history", methods=["GET"], endpoint="history")
@login_auth
def history_page():
    page = request.args.get("page", 1, type=int)
    page_sum = LabelService.page_count_my_alarms(session["id"], True)
    alarm_id_list = LabelService.get_my_alarms(session["id"], True, page)
    alarm_list = [merge_alarm(alarm_id) for alarm_id in alarm_id_list]
    history_nav_list = deepcopy(worker_nav_list)
    history_nav_list[1]["active"] = True
    return render_template("worker_history.html", title="标记历史", nav_list=history_nav_list, username=session["username"],
                           alarm_list=alarm_list, page_config=get_page_config(page, page_sum))


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/logout")
def logout_page():
    session.pop("username", None)
    session.pop("userType", None)
    return redirect("/login")


def get_page_config(page: int, page_sum: int, allow_show: int = 11):
    if page_sum <= allow_show:
        is_pre_symbol = False
        is_next_symbol = False

        middle_start = 2
        middle_end = page_sum - 1
    else:
        is_pre_symbol = (page > int(allow_show / 2) + 1)
        is_next_symbol = ((page_sum - page) > int(allow_show / 2) + 1)
        if not is_next_symbol:
            middle_start = page_sum - allow_show + 2
        elif not is_pre_symbol:
            middle_start = 2
        else:
            middle_start = page - int(allow_show / 2) + 2
        # middle_start = page - int(allow_show / 2) + 1 if is_pre_symbol else 2
        if not is_pre_symbol:
            middle_end = allow_show - 2
        elif not is_next_symbol:
            middle_end = page_sum - 1
        else:
            middle_end = page + int(allow_show / 2) - 2
        # middle_end = page + int(allow_show / 2) - 1 if is_next_symbol else page_sum - 1
    return {
        "active": page,
        "sum": page_sum,
        # 上一页和下一页是否可用
        "is_pre": page > 1,
        "is_next": page < page_sum,
        # 前部和后部的省略号是否显示
        "is_pre_symbol": is_pre_symbol,
        "is_next_symbol": is_next_symbol,
        "middle_start": middle_start,
        "middle_end": middle_end
    }


if __name__ == "__main__":
    app.run(debug=True, port=8080)
