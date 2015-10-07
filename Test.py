#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from TextProc.CommentReplace import *
from TextProc.GeneralReplace import *
from TextProc.TextProcessor import *

if __name__ == '__main__':
    def handle(content):
        return content.replace('****Die****', '****Live****')

    # t = TextProcessor('./test/a')
    # t.addReplace(ASingleLineComment)
    # t.addReplace(CSingleLineComment)
    # t.addReplace(CMultiLineComment)
    # t.addReplace(AMultiLineComment)
    # t.addReplace(ALiteralString)
    # t.addReplace(DLiteralString)
    # t.addHandle(handle)
    # t.sequenceProcess()

    t = TextProcessor('./test/a')
    t.addReplace(ASingleLineComment)
    t.addReplace(CSingleLineComment)
    t.addReplace(CMultiLineComment)
    t.addReplace(AMultiLineComment)
    t.addReplace(ALiteralString)
    t.addReplace(DLiteralString)
    t.addHandle(handle)
    t.centerProcess()