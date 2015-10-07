# TextProcess

在对代码文件进行文本处理时，如果仅仅想偷懒不想从编译器的角度写处理程序，需要考虑很多特殊情况。比如注释与字符串是不受语法限制的。该工具的作用就是将文本文件中，*存在的干扰项进行替换*，当完成文本处理程序后，*恢复先前的替换*。


## 使用方式

### 对注释进行替换

注释替换就是删除，所以不一定能完全恢复。如果对存在注释的行进行过修改，那么改行的注释就不能恢复，会被丢弃。提供的注释替换类为 `SingleLineCommentReplace`, `MultiLineCommentReplace`。已实现的注释有：

```
ASingleLineComment = SingleLineCommentReplace('#')      # Python 单行注释
CSingleLineComment = SingleLineCommentReplace('//')     # C 语言单行注释
AMultiLineComment = MultiLineCommentReplace('<!--', '-->', True)    # HTML 多行注释
BMultiLineComment = MultiLineCommentReplace('/\*', '\*/', True)     # C 语言多行注释，可嵌套
CMultiLineComment = MultiLineCommentReplace('/\*', '\*/', False)    # C 语言多行注释，不嵌套
```

### 一般替换
一般替换是将存在的干扰项替换为唯一的ID，因为ID的唯一性，所以该替换可完全恢复。通常只需继承 `GeneralReplace` 并重写 `find` 方法即可。已实现的替换有 `LiteralStringReplace`：

```
ALiteralString = LiteralStringReplace('@"', '"', False)     # OC 字符串 @""
BLiteralString = LiteralStringReplace("'", "'", False)      # Py 字符串 ''
CLiteralString = LiteralStringReplace('"', '"', False)      # C 字符串 ""
DLiteralString = LiteralStringReplace('"""', '"""', True)   # Py 字符串 """ """
ELiteralString = LiteralStringReplace("'''", "'''", True)   # Py 字符串 ''' '''
```
### 使用

只需使用 `TextProcessor` 类。

- `addReplace` 方法，添加一个替换。
- `addHandle` 方法，添加一个文本处理。方法参数为 *原文本内容*，返回值为 *处理后的内容*。
- `sequenceProcess` 方法，执行处理，所有 `addReplace` 中添加的替换将按添加的顺序进行替换操作。
- `centerProcess` 方法，执行处理。所有 `addReplace` 中添加的替换将集中进行一次替换。*一般选这个哒~*






