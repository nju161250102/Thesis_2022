package model;

import com.alibaba.fastjson.annotation.JSONField;
import lombok.Data;

@Data
public class Alarm {

    public static final int UNKNOWN = -1;
    public static final int FP = 0;
    public static final int TP = 1;

    private String category = "";
    private String type = "";
    private Integer priority = -1;
    private Integer rank = -1;
    private String path = "";
    @JSONField(name = "class_name")
    private String className = "";
    private String method = "";
    private String signature = "";
    private Integer location = -1;
    private Integer label = Alarm.UNKNOWN;
    private String version;
}
