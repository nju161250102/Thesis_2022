class FeatureType(object):
    """
    保存代码中使用的所有特征类型，变量名以F开头
    """

    @staticmethod
    def to_list():
        """
        :return: 所有特征类型名称
        """
        return list(map(lambda s: getattr(FeatureType, s), filter(lambda s: s.startswith("F"), dir(FeatureType))))

    # --- Code Characteristic ---
    # *注：原论文中的文件级别均被替换为类级别
    # F19 number of non-comment source code statements in method
    F19 = "code_method_statement"
    # *F20 number of non-comment source code statements in class
    F20 = "code_class_statement"
    # F21 number of non-comment source code statements in package
    F21 = "code_package_statement"
    # *F22 number of comment lines in class
    F22 = "code_class_comment"
    # *F23 ratio of comment length and code length in class
    F23 = "code_class_comment_ratio"
    # *F28 number of methods in class
    F28 = "code_class_method"
    # F29 number of methods in package
    F29 = "code_package_method"
    # F31 number of classed in package
    F31 = "code_package_class"
    # F32 space indenting warned line
    F32 = "code_indentation"
    # F33 cyclomatic complexity
    F33 = "code_cyclomatic_complexity"

    # --- Code Analysis ---
    # F84 method visibility
    F84_public = "method_visibility_public"
    F84_default = "method_visibility_default"
    F84_protected = "method_visibility_protected"
    F84_private = "method_visibility_private"
    # F85 return type
    F85 = "return_type"
    # F86 is static/final/abstract/protected
    F86_static = "method_static"
    F86_final = "method_final"
    F86_abstract = "method_abstract"
    F86_protected = "method_protected"
    # F87 class visibility
    F87_public = "class_visibility_public"
    F87_default = "class_visibility_default"
    F87_protected = "class_visibility_protected"
    F87_private = "class_visibility_private"
    # F88 is abstract/interface/enum class
    F88_abstract = "class_abstract"
    F88_interface = "class_interface"
    F88_enum = "class_enum"

    # --- Warning Characteristics ---
    # F90 warning type
    F90 = "warning_type"
    # F91 warning priority
    F91 = "warning_priority"
    # F92 warning rank
    F92 = "warning_rank"
    # F94 number of warnings in the method
    F94 = "warning_num_method"
    # F95 number of warnings in the class
    F95 = "warning_num_class"
    # F96 number of warnings in the package
    F96 = "warning_num_package"
