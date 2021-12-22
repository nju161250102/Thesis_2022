package model;

import lombok.Data;

@Data
public class ClassInfo {

    // 可见性
    private boolean isPublic = false;
    private boolean isDefault = true;
    private boolean isProtected = false;
    private boolean isPrivate = false;
    // 修饰符
    private boolean isAbstract = false;
    private boolean isFinal = false;
    // 类型
    private boolean isInterface = false;
    private boolean isEnum = false;

}
