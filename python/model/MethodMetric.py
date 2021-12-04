from xml.etree.ElementTree import Element


class MethodMetric(object):
    """
    方法级别度量指标
    """

    def __init__(self, item: Element):
        self.name = item.findtext("name")
        self.statement_num = int(item.findtext("numberOfStatements"))
        self.complexity = int(item.findtext("cyclomaticComplexity"))
