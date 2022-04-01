"""
创建数据库脚本

在当前目录下创建`default.db`，如果已存在则会清空。可以通过`-i`选项从实验的结果中导入数据。

短选项 | 长选项 | 参数 | 含义 | 默认值
----- | ----- | --- | --- | -----
-i | --import-data  | | 是否从实验数据中导入 | 不使用为False
-w | --worker  | WORKER_NUM | 随机工人数目 | 10

"""
import argparse
import sqlite3
import random
from faker import Faker
from model import *
from utils import DataUtils, PathUtils

faker = Faker()


def refresh():
    conn = sqlite3.connect("default.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS worker;")
    c.execute('''
        CREATE TABLE worker (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          name TEXT DEFAULT NULL,
          email TEXT DEFAULT NULL,
          password TEXT DEFAULT NULL);
        ''')
    c.execute("DROP TABLE IF EXISTS project;")
    c.execute('''
        CREATE TABLE project (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          name TEXT DEFAULT NULL,
          version TEXT DEFAULT NULL,
          state INTEGER NOT NULL,
          create_time TEXT DEFAULT NULL,
          description TEXT DEFAULT NULL);
        ''')
    c.execute("DROP TABLE IF EXISTS alarm;")
    c.execute('''
        CREATE TABLE alarm (
          id TEXT NOT NULL PRIMARY KEY,
          project_id INTEGER NOT NULL,
          category TEXT DEFAULT NULL,
          type TEXT DEFAULT NULL,
          rank INTEGER NOT NULL,
          path TEXT DEFAULT NULL,
          classname TEXT DEFAULT NULL,
          method TEXT DEFAULT NULL,
          signature TEXT DEFAULT NULL,
          location INTEGER DEFAULT -1,
          create_time TEXT DEFAULT NULL);
        ''')
    c.execute("DROP TABLE IF EXISTS label;")
    c.execute('''
        CREATE TABLE label (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          alarm_id TEXT NOT NULL,
          worker_id INTEGER NOT NULL,
          value INTEGER NOT NULL ,
          label_time TEXT DEFAULT NULL,
          create_time TEXT DEFAULT NULL);
        ''')


def generate_worker(worker_num: int):
    for _ in range(worker_num):
        WorkerModel.create(
            name=faker.first_name(),
            email=faker.ascii_company_email(),
            password=faker.pystr(faker.pyint(8, 12))
        )


def generate_project(project_config, last_state: int):
    version_dict = {}
    time_dict = {}
    for index, version in enumerate(project_config.select):
        for v in project_config.versions:
            if v.number == version:
                project = ProjectModel.create(
                    name=project_config.name,
                    version=version,
                    create_time=v.updateTime.strftime("%Y-%m-%d %H:%M:") + str(faker.pyint(10, 59)),
                    description=v.target,
                    state=2 if index < len(project_config.select) - 1 else last_state
                )
                version_dict[version] = project.id
                time_dict[version] = v.updateTime
    return version_dict, time_dict


def generate_alarm(project_config, version_dict, time_dict, last_state: int, worker_num: int):
    report_df = DataUtils.read_report_df(project_config)
    # 对每个版本随机构造扫描时间
    create_time_dict = {k: faker.date_time_between(start_date=v, end_date="+30d") for k, v in time_dict.items()}
    alarm_time_dict = {k: [faker.date_time_between(start_date=create_time_dict[k], end_date="+5d")
                           for _ in range(int(len(report_df) / len(project_config.select) / 50))]
                       for k, v in time_dict.items()}

    for index, row in report_df.iterrows():
        if row["label"] < 0:
            continue
        # 先构造，再保存
        alarm = AlarmModel(
            id=index,
            project_id=version_dict[row["version"]],
            category=row["category"],
            type=row["type"],
            rank=row["rank"],
            path=row["path"],
            classname=row["class_name"],
            method=row["method"],
            signature=row["signature"],
            location=row["new_location"],
            create_time=create_time_dict[row["version"]].strftime("%Y-%m-%d %H:%M:%S")
        )
        random_index = faker.pyint(0, len(alarm_time_dict[row["version"]]) - 1)
        label_create_time = alarm_time_dict[row["version"]][random_index]
        label = LabelModel(
            alarm_id=index,
            worker_id=faker.pyint(0, worker_num - 1),
            value=-1,
            create_time=label_create_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        # 判断是否为最后一个版本
        if row["version"] == project_config.select[-1]:
            # 如果处于检测中，则不会导入警告
            if last_state == 0:
                continue
            # 如果处于审核中，则导入警告，但随机决定是否标记
            if last_state == 1 and faker.pyint(1, 10) < 6:
                alarm.save()
                if random_index == 0 and faker.pyint(1, 10) < 6:
                    label.label_time = faker.date_time_between(start_date=label_create_time, end_date="+4h").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    label.value = row["label"]
                    label.save()
                continue
        alarm.save(force_insert=True)
        label.label_time = faker.date_time_between(start_date=label_create_time, end_date="+4h").strftime(
            "%Y-%m-%d %H:%M:%S")
        label.value = row["label"]
        label.save(force_insert=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Database")
    parser.add_argument("-i", "--import-data", action="store_true",
                        help="Use this option to import data from experiments result")
    parser.add_argument("-w", "--worker", action="store", default=10, type=int,
                        help="The number of workers")
    args = parser.parse_args()

    # 设置工人的数目
    _worker_num = args.worker
    # 设置检测中状态项目的数目
    _scan_num = 1
    # 所有项目配置
    _config_dict = DataUtils.read_projects(PathUtils.join_path("project.json"))
    # 检测中的项目名
    _scan_projects = random.sample(_config_dict.keys(), _scan_num)

    refresh()
    if args.import_data:
        generate_worker(_worker_num)
        for name, _project_config in _config_dict.items():
            _last_state = 2
            # 指定项目的最后一个版本设定为检测中
            if name in _scan_projects:
                _last_state = 0
            # 否则50%的概率设定为审核中，其余为审核完成
            elif faker.pybool():
                _last_state = 1
            _version_dict, _time_dict = generate_project(_project_config, _last_state)
            generate_alarm(_project_config, _version_dict, _time_dict, _last_state, _worker_num)

