# -*- coding: utf-8 -*-

from TextProc.BaseReplace import *
import re

class CommentReplace(BaseReplace):

    def __init__(self):
        super(CommentReplace, self).__init__()

    def replace(self, rawStr):
        return ''


class SingleLineCommentReplace(CommentReplace):

    def __init__(self, startStrRe):
        """
        :param startStrRe: 要符合正则表达式
        """

        super(SingleLineCommentReplace, self).__init__()
        self.startStr = startStrRe

    def find(self, content):
        reStr = self.startStr + r'.*(?:$|\Z)'
        match = re.search(reStr, content, re.M)

        if not match:
            return None

        return (match.start(0), match.group(0))

class MultiLineCommentReplace(CommentReplace):

    def __init__(self, startStrRe, endStrRe, isAllowNest=True):
        """
        :param startStrRe: 要符合正则表达式，如 '/*' 写为 '/\*'
        :param endStrRe: 要符合正则表达式，如 '*/' 写为 '\*/'
        :param isAllowNest: 是否允许嵌套注释
        """

        super(MultiLineCommentReplace, self).__init__()
        self.startStr = startStrRe
        self.endStr = endStrRe
        self.isAllowNest = isAllowNest

    def find(self, content):
        if not self.isAllowNest:
            reStr = self.startStr + r'.*?' + self.endStr
            match = re.search(reStr, content, re.S)

            if not match:
                return None

            return (match.start(0), match.group(0))
        else:
            startRe = re.compile(self.startStr)
            endRe = re.compile(self.endStr)

            startMatch = startRe.search(content)
            if not startMatch:
                return None

            count = 1
            start = startMatch.start(0)
            content = content[startMatch.start(0):]
            resultStr = content[:startMatch.end(0)]
            content = content[startMatch.end(0):]

            while content and count != 0:
                startMatch = startRe.search(content)
                endMatch = endRe.search(content)

                if (not startMatch) and (not endMatch):
                    break

                if startMatch and ((not endMatch) or startMatch.start() < endMatch.start()):
                    count = count + 1
                    resultStr += content[:startMatch.end(0)]
                    content = content[startMatch.end(0):]
                else:
                    count = count - 1
                    resultStr += content[:endMatch.end(0)]
                    content = content[endMatch.end(0):]

            if count == 0:
                return (start, resultStr)

            return None

ASingleLineComment = SingleLineCommentReplace('#')      # Python 单行注释
CSingleLineComment = SingleLineCommentReplace('//')     # C 语言单行注释

AMultiLineComment = MultiLineCommentReplace('<!--', '-->', True)    # HTML 多行注释
BMultiLineComment = MultiLineCommentReplace('/\*', '\*/', True)     # C 语言多行注释，可嵌套
CMultiLineComment = MultiLineCommentReplace('/\*', '\*/', False)    # C 语言多行注释，不嵌套

