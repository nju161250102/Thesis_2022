import re
from datetime import datetime
from typing import Dict

import requests
import wget

from Config import Config
from Logger import LOG
from model import ProjectConfig, Version
from utils import PathUtils, CommandUtils


class MavenData(object):
    """
    对 Maven 仓库的相关操作
    """

    @staticmethod
    def search_all_versions() -> Dict[str, ProjectConfig]:
        """
        从Maven仓库中收集项目的版本数据等信息，并根据设置过滤出需要的版本
        """
        result = {}
        for p, config in Config.MAVEN_URL.items():
            # 获取包含版本信息的配置数据
            info = MavenData.search_versions(config["url"])
            # 如果指定了筛选的版本，合并
            if "select" in config.keys() and len(config["select"]) > 0:
                info.select = config["select"]
            # 如果指定了保留的版本的时间范围，筛选
            select_versions = info.versions[:]
            if "startDate" in config.keys() and config["startDate"] is not None:
                start_date = datetime.strptime(config["startDate"], "%Y-%m-%d")
                select_versions = list(filter(lambda v: v.updateTime >= start_date, select_versions))
            if "endDate" in config.keys() and config["endDate"] is not None:
                end_date = datetime.strptime(config["endDate"], "%Y-%m-%d")
                select_versions = list(filter(lambda v: v.updateTime <= end_date, select_versions))
            # 将符合条件的版本号保存
            if "startDate" in config.keys() or "endDate" in config.keys():
                select_versions = list(
                    filter(lambda v: v.sources is not None and v.target is not None, select_versions))
                info.select = list(map(lambda v: v.number, select_versions))
            result[p] = info
        return result

    @staticmethod
    def search_versions(project_url: str) -> ProjectConfig:
        """
        搜索仓库路径下各版本的信息
        :param project_url: 必须以 / 结尾
        :return: 项目对应的配置数据
        """
        # 检查路径必须由/结尾
        if project_url[-1] != "/":
            LOG.error("URL format error: " + project_url)

        project_name = project_url.split("/")[-2]
        versions = []
        req = requests.get(project_url)
        LOG.info("Start search project: " + project_name)
        for match in re.finditer(r"<a(.*?)>(.*?)</a>(.*?)\n", req.text, re.DOTALL):
            if match.groups()[2].strip() != "":
                groups = re.search(r"(.+?)( {2,})(.+?)", match.groups()[2].strip()).groups()
                # 匹配结果：日期时间 空白 文件大小
                path = match.groups()[1]
                update_time = groups[0]
                file_size = groups[2]
                if file_size == "-" and update_time != "-":
                    # 进入下层目录寻找Jar包地址
                    version_number = path[:-1]
                    LOG.info(version_number)
                    # Jar包
                    target_jar = "{0}-{1}.jar".format(project_name, version_number)
                    # 源码Jar包
                    sources_jar = "{0}-{1}-sources.jar".format(project_name, version_number)
                    html = requests.get(project_url + path).text
                    # 精确匹配，暂时没写没模糊匹配
                    if target_jar not in html:
                        LOG.warn(target_jar + "not found")
                        target_jar = None
                    if sources_jar not in html:
                        LOG.warn(sources_jar + "not found")
                        sources_jar = None
                    version = Version({
                        "number": version_number,
                        "updateTime": update_time,
                        "sources": sources_jar,
                        "target": target_jar
                    })
                    if version.updateTime is not None:
                        versions.append(version)
        # 按版本发布的日期排序
        versions.sort(key=lambda v: v.updateTime)
        return ProjectConfig({
            "name": project_name,
            "url": project_url,
            "versions": versions
        })

    @staticmethod
    def download_all(project_config: Dict[str, ProjectConfig]):
        """
        下载和解压配置文件中列出的jar包
        不会重复下载已有的jar包，解压时会覆盖已有的文件
        :param project_config: 配置信息
        """
        for project, config in project_config.items():
            # 重新建立文件夹
            project_dir = PathUtils.project_path(config.name)
            PathUtils.rebuild_dir(project_dir, skip=True)
            LOG.info("Start download project: " + project)
            # 遍历下载
            for version in config.versions:
                # 检查是否需要下载
                if version.number not in config.select:
                    continue
                sources_jar = version.sources
                target_jar = version.target
                # 文件不存在则下载
                if not PathUtils.exist_path("project", config.name, sources_jar):
                    wget.download(config.url + version.number + "/" + sources_jar, project_dir, None)
                if not PathUtils.exist_path("project", config.name, target_jar):
                    wget.download(config.url + version.number + "/" + target_jar, project_dir, None)
                # 解压jar
                PathUtils.rebuild_dir(PathUtils.project_path(config.name, version.number))
                CommandUtils.run("unzip -q -d {0} {1}".format(PathUtils.project_path(config.name, version.number),
                                                              PathUtils.project_path(config.name, sources_jar)))
                LOG.info("{0} version {1} done.".format(config.name, version.number))
