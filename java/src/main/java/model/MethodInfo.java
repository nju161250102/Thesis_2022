package model;

import lombok.Data;

@Data
public class MethodInfo {

    // 可见性
    private boolean isPublic = false;
    private boolean isDefault = false;
    private boolean isProtected = false;
    private boolean isPrivate = false;
    // 修饰符
    private boolean isAbstract = false;
    private boolean isFinal = false;
    private boolean isStatic = false;
    // 返回类型
    private String returnType = "";

}
