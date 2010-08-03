# -*- coding: utf-8 -*-
import wx

if __name__=='__main__':
    app = wx.App()
    dlg = wx.FileDialog(None, u'변환할 한글 5.0 파일을 고르십시오:', '', '*.hwp', u'HWP 파일(*.hwp)|*.hwp')
    ret = dlg.ShowModal()

    if ret == 5100:
        import os.path
        doc = None
        try:
            import hwp50, hwp50html
            hwpfilename = dlg.GetPath()
            doc = hwp50.Document(hwpfilename)
        except Exception, e:
            msgdlg = wx.MessageDialog(None, u'변환할 수 없는 파일입니다.'+unicode(e))
            msgdlg.ShowModal()
        if doc is not None:
            try:
                rootname = os.path.splitext(os.path.basename(hwpfilename))[0]
                cvt = hwp50html.HtmlConverter()
                cvt.convert(doc, hwp50html.LocalDestination(rootname))
                msgdlg = wx.MessageDialog(None, u'변환하였습니다.')
                msgdlg.ShowModal()
            except Exception, e:
                msgdlg = wx.MessageDialog(None, u'변환에 실패하였습니다:'+unicode(e))
                msgdlg.ShowModal()
