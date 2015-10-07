# -*- coding: utf-8 -*-

from TextProc.Context import *
from abc import ABCMeta, abstractmethod
import codecs
import subprocess
import re


class BaseReplace(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.allRecords = []
        self.replacedPath = ''
        self.restoredPath = ''  # 在 Context 中被赋值

    @abstractmethod
    def find(self, content):
        """
        在 content 中查找需替换的串
        :return: (startPosition, str)
        """
        pass

    @abstractmethod
    def replace(self, rawStr):
        """
        :param rawStr: find 方法的返回值
        :return: 对 rawStr 替换的字符串
        """
        pass

    def record(self, rawRecord, newRecord):
        record = ReplaceRecord(rawRecord, newRecord)
        self.allRecords.append(record)
        Context().allRecords.append(record)

    def handle(self):
        '''
        对文件执行该替换
        '''
        with codecs.open(self.previousReplacedPath(), 'r', 'utf-8') as fr:
            rawContent = fr.read()
        rawText = TxtPosition()
        newText = TxtPosition()

        while True:
            foundResult = self.find(rawContent)
            if not foundResult:
                break

            start, foundStr = foundResult
            replacedStr = self.replace(foundStr)
            newText.addTxt(rawContent[:start])
            newRecord = newText.addTxt(replacedStr)

            rawText.addTxt(rawContent[:start])
            rawContent = rawContent[start:]
            rawRecord = rawText.addTxt(foundStr)
            rawContent = rawContent[len(foundStr):]

            self.record(rawRecord, newRecord)

        newContent = replaceWithRecord(self.previousReplacedPath(), self.allRecords)
        with codecs.open(self.replacedPath, 'w', 'utf-8') as fw:
            fw.write(newContent)


    def restore(self):
        """
        对 content 应用 allRecords 恢复文件
        :return: 返回恢复后的结果
        """
        newContent = restoreFile(self.replacedPath, self.restoredPath, self.allRecords)
        with codecs.open(self.nextRestoredPath(), 'w', 'utf-8') as fw:
            fw.write(newContent)

    def previousReplacedPath(self):
        return Context().getPreviousReplacedPath(self)

    def nextReplacedPath(self):
        return Context().getNextReplacedPath(self)

    def previousRestoredPath(self):
        return Context().getPreviousRestoredPath(self)

    def nextRestoredPath(self):
        return Context().getNextRestoredPath(self)


class TxtRecord(object):
    """
    记录文本中的字符串的位置
    """

    def __init__(self, row=0, col=0, txt=''):
        self.row = row
        self.col = col
        self.txt = txt


class ReplaceRecord(object):
    """
    字符串的替换记录
    """

    def __init__(self, rawRecord=TxtRecord(), newRecord=TxtRecord()):
        self.rawRecord = rawRecord
        self.newRecord = newRecord


class TxtPosition(object):
    """
    生成 TxtRecord
    """

    def __init__(self):
        self.row = 1
        self.col = 0

    def addTxt(self, txt):
        lines = txt.split('\n')
        row = self.row
        col = self.col

        self.row += len(lines) - 1
        if len(lines) == 1:
            self.col += len(lines[-1])
        else:
            self.col = len(lines[-1])

        return TxtRecord(row, col, txt)

def replaceWithRecord(rawFilePath, allRecords):
    """
    对 rawFilePath 应用 allRecords
    """

    with codecs.open(rawFilePath, 'r', 'utf-8') as fr:
        rawContent = fr.read()

    rawText = TxtPosition()
    newContent = ''
    recordIdx = 0
    endPos = 0
    while True:
        if (recordIdx == len(allRecords)) or (endPos == len(rawContent)):
            newContent += rawContent
            break

        rawRecord = allRecords[recordIdx].rawRecord
        newRecord = allRecords[recordIdx].newRecord

        if rawText.row == rawRecord.row and rawText.col == rawRecord.col:
            newContent += rawContent[:endPos]
            rawContent = rawContent[endPos:]
            endPos = 0

            newContent += newRecord.txt
            rawContent = rawContent[len(rawRecord.txt):]
            rawText.addTxt(rawRecord.txt)

            recordIdx = recordIdx + 1
            continue

        rawText.addTxt(rawContent[endPos])
        endPos = endPos + 1

    return newContent

def getDiffLineDict(rawFilePath, newFilePath):
    """
    用 diff -u 命令得到改动后 file2 相对于 file1，每行的对应情况
    :return: 返回列表，lineDict[a] = b，代表 file2 的第 a 行对应 file1 的第 b 行。
    如果，b = 0，表示 file2 的该行为新增或修改过
    """

    cmd = ['diff', '-u', rawFilePath, newFilePath]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    diffResult = proc.stdout.read()

    reStr = r'^@@ -\d*,\d* \+\d*,\d* @@$\n'
    diffGroups = iter(re.split(reStr, diffResult, flags=re.M)[1:])

    rawSubLines = []
    newAddLines = []
    reStr = r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@$'
    for match in re.finditer(reStr, diffResult, flags=re.M):
        rawStart = int(match.group(1))
        newStart = int(match.group(3))
        rawLineNumber = rawStart
        newLineNumber = newStart

        for line in next(diffGroups).split('\n'):
            if line.startswith('-'):
                rawSubLines.append(rawLineNumber)
                rawLineNumber = rawLineNumber + 1
            elif line.startswith('+'):
                newAddLines.append(newLineNumber)
                newLineNumber = newLineNumber + 1
            elif line.startswith(' '):
                rawLineNumber = rawLineNumber + 1
                newLineNumber = newLineNumber + 1

    rawSubLines = set(rawSubLines)
    newAddLines = set(newAddLines)
    rawLineNumber = 1

    with codecs.open(newFilePath, 'r', 'utf-8') as fr:
        rawContent = fr.read()
    lineDict = [0]

    for newLineNumber in range(1, rawContent.count('\n') + 2):
        lineDict.append(0)
        if newAddLines.intersection(set([newLineNumber])):
            continue

        while rawSubLines.intersection(set([rawLineNumber])):
            rawLineNumber = rawLineNumber + 1

        lineDict[-1] = rawLineNumber
        rawLineNumber = rawLineNumber + 1

    return lineDict

def restoreWithLineDict(newFilePath, allRecords, lineDict):
    """
    通过 allRecords 和 lineDict 来恢复 newFilePath
    返回恢复后的 rawContent
    """
    with codecs.open(newFilePath, 'r', 'utf-8') as fr:
        newContent = fr.read()
    rawContent = ''

    rawText = TxtPosition()
    recordIdx = 0
    endPos = 0
    while True:
        if (recordIdx == len(allRecords)) or (endPos == len(newContent)):
            rawContent += newContent
            break

        rawRecord = allRecords[recordIdx].rawRecord
        newRecord = allRecords[recordIdx].newRecord
        while newRecord.row < rawText.row:
            recordIdx = recordIdx + 1
            rawRecord = allRecords[recordIdx].rawRecord
            newRecord = allRecords[recordIdx].newRecord

        if rawText.row == newRecord.row and rawText.col == newRecord.col:
            recordIdx = recordIdx + 1
            if lineDict[rawText.row]:
                rawContent += newContent[:endPos]
                newContent = newContent[endPos:]
                endPos = 0

                rawContent += rawRecord.txt
                newContent = newContent[len(newRecord.txt):]
                rawText.addTxt(newRecord.txt)

            continue

        rawText.addTxt(newContent[endPos])
        endPos = endPos + 1

    return rawContent


def restoreFile(rawFilePath, newFilePath, allRecords):
    """
    对 newFilePath 应用 allRecords 恢复为 rawFilePath
    """
    lineDict = getDiffLineDict(rawFilePath, newFilePath)
    return restoreWithLineDict(newFilePath, allRecords, lineDict)