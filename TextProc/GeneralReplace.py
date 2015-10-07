# -*- coding: utf-8 -*-

from TextProc.BaseReplace import *
import re
import uuid

class GeneralReplace(BaseReplace):

    def __init__(self):
        super(GeneralReplace, self).__init__()

    def replace(self, rawStr):
        """
        一般你不用重写该方法，如果重写需保证该方法返回结果唯一性和复杂性，该类会在 TextProcessor 被全局恢复。
        """

        return 'TP_' + str(uuid.uuid1())


class LiteralStringReplace(GeneralReplace):

    def __init__(self, startStrRe, endStrRe, isMultiLine=False):
        """
        :param startStrRe: 字符串开始符号，传入正则形式
        :param endStrRe: 字符串结束符号，传入正则形式
        :param isMultiLine: 字符串是否支持换行
        """

        super(LiteralStringReplace, self).__init__()
        self.startStr = startStrRe
        self.endStr = endStrRe
        self.isMultiLine = isMultiLine

    def find(self, content):
        reStr = self.startStr + r'.*?(?<!\\)' + self.endStr

        if not self.isMultiLine:
            match = re.search(reStr, content)
        else:
            match = re.search(reStr, content, re.S)

        if not match:
            return None

        return (match.start(0), match.group(0))


ALiteralString = LiteralStringReplace('@"', '"', False)     # OC 字符串 @""
BLiteralString = LiteralStringReplace("'", "'", False)      # Py 字符串 ''
CLiteralString = LiteralStringReplace('"', '"', False)      # C 字符串 ""
DLiteralString = LiteralStringReplace('"""', '"""', True)   # Py 字符串 """ """
ELiteralString = LiteralStringReplace("'''", "'''", True)   # Py 字符串 ''' '''
