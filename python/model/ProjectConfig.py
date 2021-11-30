from Logger import LOG
from .Version import Version


class ProjectConfig(object):

    def __init__(self, config: dict):
        try:
            self.name = config["name"]
            self.url = config["url"]
            # 如果是字典则转换
            self.versions = list(map(lambda v: Version(v) if type(v) == dict else v, config["versions"]))
            self.select = config.get("select", None)
        except KeyError as e:
            LOG.error("No key {0} in input dictionary".format(e))
