import re
from typing import Dict

import requests
import wget

from model import ProjectConfig, Version
from utils import LOG, PathUtils, CommandUtils


class MavenData(object):
    """
    对 Maven 仓库的相关操作
    """

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
        for match in re.finditer(r"<a(.*?)>(.*?)</a>(.*?)<", req.text, re.DOTALL):
            if match.groups()[2].strip() != "":
                groups = re.search(r"(.+?)( {2,})(.+?)", match.groups()[2].strip()).groups()
                # 匹配结果：日期时间 空白 文件大小
                path = match.groups()[1]
                update_time = groups[0]
                file_size = groups[2]
                if file_size == "-":
                    # 进入下层目录寻找Jar包地址
                    version = path[:-1]
                    # Jar包
                    target_jar = "{0}-{1}.jar".format(project_name, version)
                    # 源码Jar包
                    sources_jar = "{0}-{1}-sources.jar".format(project_name, version)
                    html = requests.get(project_url + path).text
                    # 精确匹配，暂时没写没模糊匹配
                    if target_jar not in html:
                        LOG.warn(target_jar + "not found")
                        target_jar = None
                    if sources_jar not in html:
                        LOG.warn(sources_jar + "not found")
                        sources_jar = None
                    LOG.info(version)
                    versions.append(Version({
                        "number": version,
                        "updateTime": update_time,
                        "sources": sources_jar,
                        "target": target_jar
                    }))
        # 按版本发布的日期排序
        versions.sort(key=lambda v: v["updateTime"])
        return ProjectConfig({
            "name": project_name,
            "url": project_url,
            "versions": versions
        })

    @staticmethod
    def download_all(project_config: Dict[str, ProjectConfig]):
        """
        下载配置文件中列出的jar包
        :param project_config: 配置信息
        """
        for project, config in project_config.items():
            # 重新建立文件夹
            project_dir = PathUtils.join_path("project", config.name)
            PathUtils.rebuild_dir(project_dir)
            LOG.info("Start download project: " + project)
            # 遍历下载
            for version in config.versions:
                # 指定了需要下载的版本
                if version.number not in config.select:
                    continue
                sources_jar = version["sources"]
                target_jar = version["target"]
                wget.download(config.url + version.number + "/" + sources_jar, project_dir)
                wget.download(config.url + version.number + "/" + target_jar, project_dir)
                # 解压jar
                CommandUtils.run("unzip -q -d {0} {1}".format(PathUtils.project_path(config.name, version.number),
                                                              PathUtils.project_path(config.name, sources_jar)))
                LOG.info("{0} version {1} done.".format(config.name, version.number))
