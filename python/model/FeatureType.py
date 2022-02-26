from typing import List


class _FeatureType(object):

    def __init__(self, name: str, type_flag: int, select_flag: bool):
        """
        :param name: 特征名
        :param type_flag: 特征类型标识：0-有限取值（二值）；1-一般值；2-字符串
        :param select_flag: 是否被选择用于模型训练
        """
        self.name = name
        self.type_flag = type_flag
        self.select_flag = select_flag

    def __str__(self):
        return self.name


class FeatureType(object):
    """
    保存代码中使用的所有特征类型，变量名以F开头
    """

    @staticmethod
    def to_list(type_flag: int = -1) -> List[_FeatureType]:
        """
        :type_flag 特征类型标识
        :return: 符合条件的所有特征，默认返回所有
        """
        result = list(filter(lambda a: type(a) == _FeatureType, map(lambda s: getattr(FeatureType, s), dir(FeatureType))))
        if type_flag < 0:
            return result
        else:
            return list(filter(lambda a: a.type_flag == type_flag, result))

    @staticmethod
    def to_str_list(type_list: List[_FeatureType] = None):
        """
        :return: 特征类型的名称，默认返回所有
        """
        if type_list:
            return list(map(lambda a: a.name, type_list))
        else:
            return list(map(lambda a: a.name, FeatureType.to_list()))

    @staticmethod
    def get_label(feature: str) -> str:
        """
        :return: 特征对应的编号
        """
        for label, f in map(lambda s: (s, getattr(FeatureType, s)), dir(FeatureType)):
            if f.name == feature:
                return label
        return ""

    # --- Code Characteristic ---
    # *注：原论文中的文件级别均被替换为类级别
    # F19 number of non-comment source code statements in method
    F19 =               _FeatureType("code_method_statement",       1, True)
    # *F20 number of non-comment source code statements in class
    F20 =               _FeatureType("code_class_statement",        1, True)
    # F21 number of non-comment source code statements in package
    F21 =               _FeatureType("code_package_statement",      1, True)
    # *F22 number of comment lines in class
    F22 =               _FeatureType("code_class_comment",          1, True)
    # *F23 ratio of comment length and code length in class
    F23 =               _FeatureType("code_class_comment_ratio",    1, True)
    # *F28 number of methods in class
    F28 =               _FeatureType("code_class_method",           1, True)
    # F29 number of methods in package
    F29 =               _FeatureType("code_package_method",         1, True)
    # F31 number of classed in package
    F31 =               _FeatureType("code_package_class",          1, True)
    # F32 space indenting warned line
    F32 =               _FeatureType("code_indentation",            1, True)
    # F33 cyclomatic complexity
    F33 =               _FeatureType("code_cyclomatic_complexity",  1, True)

    # --- Code Analysis ---
    # F84 method visibility
    F84_public =        _FeatureType("method_visibility_public",    0, True)
    F84_default =       _FeatureType("method_visibility_default",   0, True)
    F84_protected =     _FeatureType("method_visibility_protected", 0, True)
    F84_private =       _FeatureType("method_visibility_private",   0, True)
    # F85 return type
    F85 =               _FeatureType("return_type",                 2, True)
    # F86 is static/final/abstract/protected
    F86_static =        _FeatureType("method_static",               0,  True)
    F86_final =         _FeatureType("method_final",                0,  True)
    F86_abstract =      _FeatureType("method_abstract",             0,  True)
    F86_protected =     _FeatureType("method_protected",            0,  True)
    # F87 class visibility
    F87_public =        _FeatureType("class_visibility_public",     0,  True)
    F87_default =       _FeatureType("class_visibility_default",    0,  True)
    F87_protected =     _FeatureType("class_visibility_protected",  0,  True)
    F87_private =       _FeatureType("class_visibility_private",    0,  True)
    # F88 is abstract/interface/enum class
    F88_abstract =      _FeatureType("class_abstract",              0,  True)
    F88_interface =     _FeatureType("class_interface",             0,  True)
    F88_enum =          _FeatureType("class_enum",                  0,  True)

    # --- Warning Characteristics ---
    # F90 warning type
    F90 =               _FeatureType("warning_type",                2, True)
    # F91 warning priority
    F91 =               _FeatureType("warning_priority",            1, True)
    # F92 warning rank
    F92 =               _FeatureType("warning_rank",                1, True)
    # F94 number of warnings in the method
    F94 =               _FeatureType("warning_num_method",          1, True)
    # F95 number of warnings in the class
    F95 =               _FeatureType("warning_num_class",           1, True)
    # F96 number of warnings in the package
    F96 =               _FeatureType("warning_num_package",         1, True)

    # --- Warning Combination ---
    # F112 defect likelihood for warning pattern
    F112 =              _FeatureType("warning_pattern_likelihood",  1, True)
    # F113 variance of likelihood
    F113 =              _FeatureType("warning_likelihood_variance", 1, True)
    # F114 defect likelihood for warning type
    F114 =              _FeatureType("warning_type_likelihood",     1, True)
    # F115 discretization of defect likelihood
    F115 =              _FeatureType("warning_discretization",      1, True)
