import com.github.javaparser.Range;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.comments.Comment;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
public class JavaFormatter {

    /**
     * 对java文件重新格式化，并找到处理后代码行的位置
     * @param originalPath 原始文件路径
     * @param newPath 修改后的文件路径
     * @param lines 原文件中代码行位置
     * @return 处理后代码行的位置
     */
    public static List<Integer> formatFile(Path originalPath, Path newPath, List<Integer> lines) {
        try {
            // 开始处理
            CompilationUnit cu = StaticJavaParser.parse(originalPath);
            List<Integer> result = lines.stream()
                    .map(line -> {
                        // 保存目标节点
                        final Node[] node = {null};
                        CompilationUnit copy_cu = cu.clone();
                        // 层次遍历寻找包含代码行的最小树节点
                        copy_cu.walk(Node.TreeTraversal.BREADTHFIRST, n -> {
                            Range range = n.getRange().orElse(null);
                            if (range != null && node[0] == null && range.begin.line == line && range.end.line == line) {
                                node[0] = n;
                            }
                        });
                        // 去除注释
                        copy_cu.removeComment().getAllContainedComments().forEach(Comment::remove);
                        // 为节点增加特有的行注释，再到之后的文本中查找
                        String flagStr = Integer.toString(node[0].toString().hashCode());
                        node[0].setLineComment(flagStr);
                        String[] _lines = copy_cu.toString().split("\n");
                        for (int i = 0; i < _lines.length; i++) {
                            if (_lines[i].endsWith(flagStr)) {
                                return i + 1;
                            }
                        }
                        return -1;
                    })
                    .collect(Collectors.toList());
            if (result.stream().anyMatch(i -> i != -1)) {
                cu.removeComment().getAllContainedComments().forEach(Comment::remove);
                String[] original_lines = cu.toString().split("\n");
                // 创建新文件并保存内容
                FileUtils.forceMkdirParent(newPath.toFile());
                FileUtils.touch(newPath.toFile());
                FileUtils.writeLines(newPath.toFile(), Arrays.asList(original_lines));
            }
            return result;
        } catch (IOException e) {
            log.error("Parse java file error: " + originalPath);
            e.printStackTrace();
            return Collections.nCopies(-1, lines.size());
        }
    }
}
