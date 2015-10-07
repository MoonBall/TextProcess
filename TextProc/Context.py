# -*- coding: utf-8 -*-

import TextProc.BaseReplace
import os
import shutil

class Singleton(object):

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

class Context(Singleton):
    """
    这里面只保存信息，不做任何与文本内容相关的操作，所有属性外部不可修改
    """

    def __init__(self, fpath=None):
        if not fpath:
            return

        self.fname = os.path.basename(fpath)
        self.dirpath = os.path.join(os.path.dirname(fpath), 'TextProcResult')
        if not os.path.exists(self.dirpath):
            os.mkdir(self.dirpath)

        self.replacedPath = self.__tempFile('_r')
        self.handledPath = self.__tempFile('_h')
        self.restoredPath = self.__tempFile('_s')
        self.resultPath = self.__tempFile('')
        shutil.copyfile(fpath, self.resultPath)

        self.replaces = []
        self.handles = []
        self.allRecords = []

    def addReplaces(self, replaces):
        for replace in replaces:
            self.addReplace(replace)

    def addReplace(self, replace):

        if not isinstance(replace, TextProc.BaseReplace.BaseReplace):
            raise TypeError('replace should be type of BaseReplace')
        self.replaces.append(replace)
        replace.replacedPath = self.__replacedPath(len(self.replaces))
        replace.restoredPath = self.__restoredPath(len(self.replaces))

    def addHandles(self, handles):
        for handle in handles:
            self.addHandle(handle)

    def addHandle(self, handle):
        if not hasattr(handle, '__call__'):
            raise TypeError('handle should be function')
        self.handles.append(handle)

    def getPreviousReplacedPath(self, replace):
        idx = self.replaces.index(replace)
        if idx == 0:
            return self.resultPath
        return self.replaces[idx - 1].replacedPath

    def getNextReplacedPath(self, replace):
        idx = self.replaces.index(replace)
        if idx == len(self.replaces) - 1:
            return self.handledPath
        return self.replaces[idx + 1].replacedPath

    def getPreviousRestoredPath(self, replace):
        idx = self.replaces.index(replace)
        if idx == len(self.replaces) - 1:
            return self.handledPath
        return self.replaces[idx + 1].restoredPath

    def getNextRestoredPath(self, replace):
        idx = self.replaces.index(replace)
        if idx == 0:
            return self.resultPath
        return self.replaces[idx - 1].restoredPath

    def clean(self):
        def removeFile(path):
            if os.path.exists(path):
                os.remove(path)

        for replace in self.replaces:
            removeFile(replace.replacedPath)
            removeFile(replace.restoredPath)

        removeFile(self.replacedPath)
        removeFile(self.restoredPath)
        removeFile(self.handledPath)

    def __tempFile(self, suffix):
        nameExt = list(os.path.splitext(self.fname))
        nameExt[0] += suffix

        return os.path.join(self.dirpath, ''.join(nameExt))

    def __replacedPath(self, idx=''):
        return self.__tempFile('_r_' + str(idx))

    def __restoredPath(self, idx=''):
        return self.__tempFile('_s_' + str(idx))


