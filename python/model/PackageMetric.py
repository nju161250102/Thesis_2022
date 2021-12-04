from xml.etree.ElementTree import Element


class PackageMetric(object):
    """
    包级别度量指标
    """

    def __init__(self, item: Element):
        self.name = item.findtext("name")
        self.class_num = int(item.findtext("numberOfClasses"))
        self.method_num = int(item.findtext("numberOfMethods"))
        self.statement_num = int(item.findtext("numberOfStatements"))
