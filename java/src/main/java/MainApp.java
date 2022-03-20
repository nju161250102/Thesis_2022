import com.alibaba.fastjson.JSONObject;
import model.Alarm;

import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class MainApp {

    /**
     * 程序主入口
     * @param args 运行参数
     */
    public static void main(String[] args) {
        if (args.length < 2) {
            System.exit(1);
        }
        switch (args[0]) {
            case "format":
                List<Integer> lines = Arrays.asList(args)
                        .subList(2, args.length)
                        .stream()
                        .map(Integer::parseInt)
                        .collect(Collectors.toList());
                String output = JavaFormatter.formatFile(Paths.get(args[1]), lines)
                        .stream()
                        .map(String::valueOf)
                        .collect(Collectors.joining("\n"));
                System.out.println(output);
                return;
            case "method":
                JavaAnalyzer analyzer = new JavaAnalyzer(args[1], JSONObject.parseObject(args[2], Alarm.class));
                System.out.println(JSONObject.toJSONString(analyzer));
                return;
            default:
                System.exit(1);
        }
    }
}
