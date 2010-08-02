# -*- coding: utf-8 -*-
import wx

app = wx.App()
dlg = wx.FileDialog(None, '변환할 한글 5.0 파일을 고르십시오:', '', '*.hwp', 'HWP 파일(*.hwp)|*.hwp')
ret = dlg.ShowModal()

if ret == 5100:
    import hwp50, hwp50html
    import os.path
    doc = None
    try:
        hwpfilename = dlg.GetPath()
        doc = hwp50.Document(hwpfilename)
    except Exception, e:
        print '변환할 수 없는 파일입니다..'+str(e)
    if doc is not None:
        rootname = os.path.splitext(os.path.basename(hwpfilename))[0]
        cvt = hwp50html.HtmlConverter()
        cvt.convert(doc, hwp50html.LocalDestination(rootname))
