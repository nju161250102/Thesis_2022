import re

import requests
import wget

from utils import LOG, PathUtils, CommandUtils


class MavenData(object):

    @staticmethod
    def search_versions(project_url: str):
        """
        搜索仓库路径下各版本的信息
        :param project_url: 必须以 / 结尾
        :return: 各版本数据
        """
        result = {}
        project_name = project_url.split("/")[-2]
        req = requests.get(project_url)
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
                    # 精确匹配
                    if target_jar not in html:
                        LOG.warn(target_jar + "not found")
                        target_jar = None
                    if sources_jar not in html:
                        LOG.warn(sources_jar + "not found")
                        sources_jar = None
                    LOG.info(version)
                    result[version] = {
                        "updateTime": update_time,
                        "sources": sources_jar,
                        "target": target_jar
                    }
        return result

    @staticmethod
    def download_all(project_config: dict):
        """
        下载配置文件中列出的jar包
        :param project_config: 配置信息
        """
        for project, config in project_config.items():
            # 指定了所选择的版本
            if "select" in config.keys():
                versions = config["select"]
            # 未指定时自动选择时间范围内的版本
            else:
                versions = list(config["versions"].items())
                versions.sort(key=lambda v: v[1]["updateTime"])
                versions = list(map(lambda v: v[0], versions))
            # 重新建立文件夹
            project_dir = PathUtils.join_path("project", config["name"])
            PathUtils.rebuild_dir(project_dir)
            # 遍历下载
            for version in versions:
                sources_jar = config["versions"][version]["sources"]
                target_jar = config["versions"][version]["target"]
                wget.download(config["url"] + version + "/" + sources_jar, project_dir)
                wget.download(config["url"] + version + "/" + target_jar, project_dir)
                # 解压jar
                CommandUtils.run("unzip -q -d {0} {1}".format(PathUtils.project_path(config["name"], version),
                                                              PathUtils.project_path(config["name"], sources_jar)))
                LOG.info("{0} version {1} done.".format(config["name"], version))
