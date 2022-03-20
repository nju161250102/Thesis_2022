import com.github.javaparser.Range;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.*;
import lombok.Data;
import model.Alarm;

import java.io.IOException;
import java.nio.file.Paths;

@Data
public class JavaAnalyzer {

    // 标记方法和类的特征是否可用，处理过程是否出错
    private boolean classAvailable = false;
    private boolean methodAvailable = false;
    private String classVisibility = "default";
    private String methodVisibility = "default";
    private String returnType;
    private boolean isClassAbstract = false;
    private boolean isClassFinal = false;
    private boolean isClassInterface = false;
    private boolean isClassEnum = false;
    private boolean isMethodStatic = false;
    private boolean isMethodFinal = false;
    private boolean isMethodAbstract = false;

    public JavaAnalyzer(String projectPath, Alarm alarm) {
        // 两个元素分别存放类和方法的节点
        BodyDeclaration[] declarations = new BodyDeclaration[2];
        CompilationUnit cu;
        try {
            cu = StaticJavaParser.parse(Paths.get(projectPath, alarm.getVersion(), alarm.getPath()));
        } catch (IOException e) {
            e.printStackTrace();
            return;
        }
        // 解析出真正的类名
        String className = alarm.getClassName();
        String[] arr;
        if (className.contains("$")) {
            arr = className.split("\\$");
        } else {
            arr = className.split("\\.");
        }
        className = arr[arr.length - 1];
        for (ClassOrInterfaceDeclaration declaration : cu.findAll(ClassOrInterfaceDeclaration.class)) {
            if (declaration.getNameAsString().equals(className)) {
                String methodName = alarm.getMethod();
                Integer line = alarm.getLocation();
                // 确定方法对应的节点，构造函数方法名为<init>
                if ("<init>".equals(alarm.getMethod())) {
                    for (ConstructorDeclaration constructor : declaration.findAll(ConstructorDeclaration.class)) {
                        constructor.getRange().ifPresent(range -> {
                            if (range.begin.line <= line && line <= range.end.line) {
                                declarations[1] = constructor;
                            }
                        });
                    }
                } else {
                    for (MethodDeclaration method : declaration.findAll(MethodDeclaration.class)) {
                        if (method.getNameAsString().equals(methodName)) {
                            method.getRange().ifPresent(range -> {
                                if (range.begin.line <= line && line <= range.end.line) {
                                    declarations[1] = method;
                                }
                            });
                        }
                    }
                }
                // 如果找到了方法，说明可用
                if (declarations[1] != null) {
                    declarations[0] = declaration;
                    Node[] lineNode = {null};
                    declarations[1].walk(Node.TreeTraversal.BREADTHFIRST, n -> {
                        Range range = n.getRange().orElse(null);
                        if (range != null && lineNode[0] == null && range.begin.line == line && range.end.line == line) {
                            lineNode[0] = n;
                        }
                    });

                }
            }
        }
        // 处理类
        if (declarations[0] != null) {
            this.classAvailable = true;
            if (declarations[0].isClassOrInterfaceDeclaration()) {
                ClassOrInterfaceDeclaration classOrInterface = declarations[0].asClassOrInterfaceDeclaration();
                handleClassModifiers(classOrInterface.getModifiers());
                this.isClassInterface = classOrInterface.isInterface();
            }
        }
        // 处理方法
        if (declarations[1] != null) {
            this.methodAvailable = true;
            if (declarations[1].isConstructorDeclaration()) {
                ConstructorDeclaration constructor = declarations[1].asConstructorDeclaration();
                handleMethodModifiers(constructor.getModifiers());
            } else if (declarations[1].isMethodDeclaration()) {
                MethodDeclaration method = declarations[1].asMethodDeclaration();
                handleMethodModifiers(method.getModifiers());
                this.returnType = method.getTypeAsString();
            }
        }
    }

    private void handleMethodModifiers(Iterable<Modifier> modifiers) {
        for (Modifier modifier : modifiers) {
            switch (modifier.getKeyword()) {
                case PRIVATE:
                    this.methodVisibility = "private";
                    break;
                case PUBLIC:
                    this.methodVisibility = "public";
                    break;
                case STATIC:
                    this.isMethodStatic = true;
                    break;
                case FINAL:
                    this.isMethodFinal = true;
                    break;
                case ABSTRACT:
                    this.isMethodAbstract = true;
                    break;
                case PROTECTED:
                    this.methodVisibility = "protected";
                    break;
            }
        }
    }

    private void handleClassModifiers(Iterable<Modifier> modifiers) {
        for (Modifier modifier : modifiers) {
            switch (modifier.getKeyword()) {
                case PRIVATE:
                    this.classVisibility = "private";
                    break;
                case PUBLIC:
                    this.classVisibility = "public";
                    break;
                case FINAL:
                    this.isClassFinal = true;
                    break;
                case ABSTRACT:
                    this.isClassAbstract = true;
                    break;
                case PROTECTED:
                    this.classVisibility = "protected";
                    break;
            }
        }
    }
}
