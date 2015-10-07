# -*- coding: utf-8 -*-

from TextProc.CommentReplace import *
from TextProc.GeneralReplace import *
import shutil

class TextProcessor(object):
    """
    所有处理将从 Context().resultPath 为起点开始，并已 Context().resultPath 结束。
    可多次执行 process()，每次都是在前一次的基础上执行
    """

    def __init__(self, fpath):
        Context(fpath)

        # 保证文件末存在换行，否则 diff 命令不会比较最后一行
        fr = codecs.open(Context().resultPath, 'r', 'utf-8')
        content = fr.read()
        fr.close()
        if not content.endswith('\n'):
            fw = codecs.open(Context().resultPath, 'a', 'utf-8')
            fw.write('\n')

    def process(self):
        self.sequenceProcess()

    def sequenceProcess(self):
        """
        按 replaces 的顺序依次替换
        """

        # 进行文本处理
        if Context().replaces:
            for replace in Context().replaces:
                replace.handle()
            lastReplace = Context().replaces[-1]
            shutil.copy(lastReplace.replacedPath, Context().handledPath)

            self.__handle()

            shutil.copy(Context().handledPath, lastReplace.restoredPath)
            for replace in reversed(Context().replaces):
                replace.restore()
        else:
            self.__processNoReplace()

        self.__restoreGeneralReplace()
        Context().clean()   # 注释掉，查看转换过程文件

    def centerProcess(self):
        """
        集中处理，所有 replace 是同级的
        """

        if Context().replaces:
            self.__centerReplace()
            shutil.copy(Context().replacedPath, Context().handledPath)
            self.__handle()
            shutil.copy(Context().handledPath, Context().restoredPath)
            self.__centerRestore()
        else:
            self.__processNoReplace()

        self.__restoreGeneralReplace()
        Context().clean()   # 注释掉，查看转换过程文件

    def __centerReplace(self):
        """
        集中替换
        """
        with codecs.open(Context().resultPath, 'r', 'utf-8') as fr:
            rawContent = fr.read()

        rawText = TxtPosition()
        newText = TxtPosition()
        while True:
            foundResult = None
            for replace in Context().replaces:
                curFound = replace.find(rawContent)
                if curFound and ((not foundResult) or curFound[0] < foundResult[0]):
                    foundResult = curFound
                    foundReplace = replace

            if not foundResult:
                break

            start, foundStr = foundResult
            replacedStr = foundReplace.replace(foundStr)
            newText.addTxt(rawContent[:start])
            newRecord = newText.addTxt(replacedStr)

            rawText.addTxt(rawContent[:start])
            rawContent = rawContent[start:]
            rawRecord = rawText.addTxt(foundStr)
            rawContent = rawContent[len(foundStr):]

            foundReplace.record(rawRecord, newRecord)

        newContent = replaceWithRecord(Context().resultPath, Context().allRecords)
        with codecs.open(Context().replacedPath, 'w', 'utf-8') as fw:
            fw.write(newContent)

    def __centerRestore(self):
        """
        集中恢复
        """
        newContent = restoreFile(Context().replacedPath, Context().restoredPath, Context().allRecords)
        with codecs.open(Context().resultPath, 'w', 'utf-8') as fw:
            fw.write(newContent)

    def __restoreGeneralReplace(self):
        """
        对 GeneralReplace 进行全局恢复
        """

        with codecs.open(Context().resultPath, 'r', 'utf-8') as fr:
            rawContent = fr.read()

        for replace in Context().replaces:
            if isinstance(replace, GeneralReplace):
                for record in replace.allRecords:
                    rawTxt = record.rawRecord.txt
                    newTxt = record.newRecord.txt
                    rawContent = rawContent.replace(newTxt, rawTxt)

        with codecs.open(Context().resultPath, 'w', 'utf-8') as fw:
            fw.write(rawContent)

    def __processNoReplace(self):
        shutil.copy(Context().resultPath, Context().handledPath)
        self.__handle()
        shutil.copy(Context().handledPath, Context().resultPath)

    def __handle(self):
        for handle in Context().handles:
            fr = codecs.open(Context().handledPath, 'r', 'utf-8')
            rawContent = fr.read()

            fr.close()
            fw = codecs.open(Context().handledPath, 'w', 'utf-8')
            newContent = handle(rawContent)
            fw.write(newContent)
            fw.close()

    def addReplaces(self, replaces):
        Context().addReplaces(replaces)

    def addReplace(self, replace):
        Context().addReplace(replace)

    def addHandles(self, handles):
        Context().addHandles(handles)

    def addHandle(self, handle):
        Context().addHandle(handle)

