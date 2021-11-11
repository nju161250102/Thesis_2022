import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.comments.Comment;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Slf4j
public class JavaFormatter {

    public static void main(String[] args) {
        if (args.length != 1) {
            System.exit(1);
        }
        try {
            Files.walk(Paths.get(args[0]))
                    .filter(path -> "java".equals(FilenameUtils.getExtension(path.toString())))
                    .forEach(JavaFormatter::removeComment);
        } catch (IOException e) {
            log.error("Wrong project path: " + args[0]);
            e.printStackTrace();
        }
    }

    private static void removeComment(Path path) {
        try {
            CompilationUnit cu = StaticJavaParser.parse(path);
            cu.removeComment().getAllContainedComments().forEach(Comment::remove);
            FileUtils.write(path.toFile(), cu.toString(), Charset.defaultCharset());
        } catch (IOException e) {
            log.error("Parse java file error: " + path);
            e.printStackTrace();
        }
    }
}
