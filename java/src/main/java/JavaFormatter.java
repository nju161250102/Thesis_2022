import com.github.javaparser.Range;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.comments.Comment;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;

@Slf4j
public class JavaFormatter {

    /**
     * 对java文件重新格式化，并找到处理后代码行的位置
     * @param path 文件路径
     * @param line 原文件中代码行位置
     * @return 处理后代码行的位置
     */
    public static int formatFile(Path path, final int line) {
        try {
            CompilationUnit cu = StaticJavaParser.parse(path);
            // 保存目标节点
            final Node[] node = {null};
            // 层次遍历寻找包含代码行的最小树节点
            cu.walk(Node.TreeTraversal.BREADTHFIRST, n -> {
                Range range = n.getRange().orElse(null);
                if (range != null && node[0] == null && range.begin.line == line && range.end.line == line) {
                    node[0] = n;
                }
            });
            // 去除注释
            cu.removeComment().getAllContainedComments().forEach(Comment::remove);
            // 删除节点后与原先文本比较，缺失行标记为行号
            String[] original_lines = cu.toString().split("\n");
            node[0].remove();
            String[] removed_lines = cu.toString().split("\n");
            for (int i = 0; i < removed_lines.length; i++) {
                if (! original_lines[i].equals(removed_lines[i])) {
                    FileUtils.writeLines(path.toFile(), Arrays.asList(original_lines));
                    return i + 1;
                }
            }
            return -1;
        } catch (IOException e) {
            log.error("Parse java file error: " + path);
            e.printStackTrace();
            return -1;
        }
    }
}
