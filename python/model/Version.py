from datetime import datetime

from Logger import LOG


class Version(object):

    def __init__(self, config: dict):
        try:
            self.number = config["number"]
            try:
                self.updateTime = datetime.strptime(config["updateTime"], "%Y-%m-%d %H:%M")
            except ValueError:
                self.updateTime = None
            self.sources = config["sources"]
            self.target = config["target"]
        except KeyError as e:
            LOG.error("No key {0} in input dictionary".format(e))
