import com.alibaba.fastjson.JSONObject;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.*;
import lombok.Data;
import model.ClassInfo;
import model.MethodInfo;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

@Data
public class JavaAnalyzer {

    private Map<String, ClassInfo> classMap = new HashMap<>();
    private Map<String, MethodInfo> methodMap = new HashMap<>();

    public JavaAnalyzer(String projectPath) {
        try {
            Files.walk(Paths.get(projectPath))
                    .forEach(this::accept);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public String toString() {
        StringBuilder builder = new StringBuilder();
        for (Map.Entry<String, ClassInfo> entry : classMap.entrySet()) {
            builder.append(entry.getKey())
                    .append(System.lineSeparator())
                    .append(JSONObject.toJSONString(entry.getValue()))
                    .append(System.lineSeparator());
        }
        for (Map.Entry<String, MethodInfo> entry : methodMap.entrySet()) {
            builder.append(entry.getKey())
                    .append(System.lineSeparator())
                    .append(JSONObject.toJSONString(entry.getValue()))
                    .append(System.lineSeparator());
        }
        return builder.toString();
    }

    private void accept(Path p) {
        try {
            CompilationUnit cu = StaticJavaParser.parse(p);
            // 处理方法和接口
            cu.findAll(ClassOrInterfaceDeclaration.class)
                    .forEach(d -> d.getFullyQualifiedName().ifPresent(className -> {
                        ClassInfo info = handleClass(d);
                        info.setInterface(d.isInterface());
                        classMap.put(className, info);
                    }));
            // 处理枚举类
            cu.findAll(EnumDeclaration.class)
                    .forEach(d -> d.getFullyQualifiedName().ifPresent(className -> {
                        ClassInfo info = handleClass(d);
                        info.setEnum(true);
                        classMap.put(className, info);
                    }));
            // 处理方法
            cu.findAll(MethodDeclaration.class)
                    .forEach(m -> {
                        String className = findParentClass(m).getFullyQualifiedName().orElse("");
                        String methodName = m.getNameAsString();
                        MethodInfo info = handleMethod(m);
                        info.setReturnType(m.getTypeAsString());
                        methodMap.put(className + "." + methodName, info);
                    });
            // 处理构造方法
            cu.findAll(ConstructorDeclaration.class)
                    .forEach(m -> {
                        String className = findParentClass(m).getFullyQualifiedName().orElse("");
                        methodMap.put(className + ".<init>", handleMethod(m));
                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /**
     * 处理类信息
     */
    private <T extends TypeDeclaration<T>> ClassInfo handleClass(T declaration) {
        ClassInfo info = new ClassInfo();
        for (Modifier modifier : declaration.getModifiers()) {
            switch (modifier.getKeyword()) {
                case PRIVATE:
                    info.setPrivate(true);
                case PUBLIC:
                    info.setPublic(true);
                case FINAL:
                    info.setFinal(true);
                case ABSTRACT:
                    info.setAbstract(true);
                case PROTECTED:
                    info.setProtected(true);
            }
        }
        return info;
    }

    /**
     * 处理方法信息
     */
    private <T extends CallableDeclaration<T>> MethodInfo handleMethod(T declaration) {
        MethodInfo info = new MethodInfo();
        for (Modifier modifier : declaration.getModifiers()) {
            switch (modifier.getKeyword()) {
                case PRIVATE:
                    info.setPrivate(true);
                case PUBLIC:
                    info.setPublic(true);
                case STATIC:
                    info.setStatic(true);
                case FINAL:
                    info.setFinal(true);
                case ABSTRACT:
                    info.setAbstract(true);
                case PROTECTED:
                    info.setProtected(true);
            }
        }
        return info;
    }

    /**
     * 向上寻找最近的类声明父节点
     * @param node 节点
     * @return 节点属于的类节点
     */
    private ClassOrInterfaceDeclaration findParentClass(Node node) {
        while (node != null) {
            node = node.getParentNode().orElse(null);
            if (node instanceof ClassOrInterfaceDeclaration) {
                return (ClassOrInterfaceDeclaration) node;
            }
        }
        return null;
    }

}
