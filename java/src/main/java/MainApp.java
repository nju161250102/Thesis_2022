import java.nio.file.Paths;

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
                System.out.println(JavaFormatter.formatFile(Paths.get(args[1]), Integer.parseInt(args[2])));
                return;
            default:
                System.exit(1);
        }
    }
}
