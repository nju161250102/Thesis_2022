from flask import Flask, render_template, session, request, redirect
from copy import deepcopy
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

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
    "name": "标记任务",
    "active": False,
    "url": "/"
}, {
    "name": "标记历史",
    "active": False,
    "url": "/history"
}]


@app.route("/", methods=["GET", "POST"])
def main_page():
    # 判断是否登录
    if "username" not in session:
        username = request.form.get("username")
        password = request.form.get("password")
        # 非登录请求跳转到登录页面
        if username is None or password is None:
            return redirect("/login")
        # 密码校验
        if password == "1":
            session["username"] = username
            session["userType"] = "admin" if username == "admin" else "worker"
        else:
            return render_template("login.html", info="用户名或密码错误")
    # 此时session中已有username字段，根据用户类型返回页面
    if session["userType"] == "admin":
        index_nav_list = deepcopy(admin_nav_list)
        index_nav_list[0]["active"] = True
        return render_template("admin_index.html", title="首页", nav_list=index_nav_list, username=session["username"])
    else:
        index_nav_list = deepcopy(worker_nav_list)
        index_nav_list[0]["active"] = True
        return render_template("worker_index.html", title="首页", nav_list=index_nav_list, username=session["username"])


@app.route("/upload")
def upload_page():
    upload_nav_list = deepcopy(admin_nav_list)
    upload_nav_list[1]["active"] = True
    return render_template("admin_upload.html", title="项目上传", nav_list=upload_nav_list, username=session["username"])


@app.route("/report", methods=["GET", "POST"])
def report_page():
    # 获得审核完毕的项目列表
    project_list = [{
        "id": 1,
        "name": "FuckThesis",
        "version": "0.1"
    }]
    alarm_list = None
    if request.method == "POST":
        # 获取项目下的警告列表
        alarm_list = [{

        }]
    report_nav_list = deepcopy(admin_nav_list)
    report_nav_list[2]["active"] = True
    return render_template("admin_report.html", title="查看报告", nav_list=report_nav_list, username=session["username"],
                           project_list=project_list, alarm_list=alarm_list)


@app.route("/detail/<int:alarm_id>")
def detail_page(alarm_id):

    return render_template("worker_detail.html", title="漏洞详情", nav_list=worker_nav_list, username=session["username"])


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/logout")
def logout_page():
    session.pop("username", None)
    session.pop("userType", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
