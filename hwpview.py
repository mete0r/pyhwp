#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import urllib

import Queue
import thread

import gtk
import gobject

class gtk_thread_raised(Exception):
    def __init__(self, exc):
        self.exc = exc
    def __str__(self):
        return str(self.exc)

import sys
def synchronous_gtk_message(fun):
    queue = Queue.Queue()

    class Exception:
        info = None

    def worker((function, args, kwargs)):
        try:
            queue.put(apply(function, args, kwargs))
        except:
            Exception.info = sys.exc_info()
            queue.put(Exception)

    def fun2(*args, **kwargs):
        gobject.idle_add(worker, (fun, args, kwargs))
        result = queue.get()
        if result is Exception:
            raise gtk_thread_raised(result.info)
        return result

    return fun2

def asynchronous_gtk_message(fun):
    def worker((function, args, kwargs)):
        apply(function, args, kwargs)

    def fun2(*args, **kwargs):
        gobject.idle_add(worker, (fun, args, kwargs))

    return fun2

def start_gtk_thread():
    gtk.gdk.threads_init()
    thread.start_new_thread(gtk.main, ())

def kill_gtk_thread():
    asynchronous_gtk_message(gtk.main_quit)()

def companion_gtk_thread(fun):
    def fun2(*args, **kwargs):
        start_gtk_thread()
        try:
            x = fun(*args, **kwargs) # equivalent to "apply"
        finally:
            kill_gtk_thread()
        return x
    return fun2

def prepare_hwp_html(filename, working_dir):
    from hwp import hwp50, hwp50html

    import sys, os.path
    hwpfilename = filename.decode(sys.getfilesystemencoding())
    doc = hwp50.Document(hwpfilename)

    basename = os.path.splitext(os.path.basename(hwpfilename))[0]
    rootname = os.path.join(working_dir, basename)
    #print rootname
    cvt = hwp50html.HtmlConverter()
    cvt.convert(doc, hwp50html.LocalDestination(rootname))

    # Create a proper file:// URL pointing to demo.xhtml:
    file = os.path.abspath(rootname+'.html')
    return 'file://' + urllib.pathname2url(file.encode(sys.getfilesystemencoding()))

message_queue = Queue.Queue()
class QuitApp: pass

class MainApp:
    @synchronous_gtk_message
    def make_frame(self):
        import webkit
        self.browser = webkit.WebView()

        import gtk
        window = gtk.Window()
        window.connect('destroy', quit)

        box = gtk.VBox(homogeneous=False, spacing=0)
        window.add(box)

        accel_group = gtk.AccelGroup()
        window.add_accel_group(accel_group)

        open_item = gtk.Menu()
        open_item = gtk.MenuItem('_Open')
        open_item.add_accelerator('activate',
                accel_group,
                ord('O'),
                gtk.gdk.CONTROL_MASK,
                gtk.ACCEL_VISIBLE)
        open_item.connect('activate', self.open)
        open_item.show()

        quit_item = gtk.MenuItem('_Quit')
        quit_item.add_accelerator('activate',
                accel_group,
                ord('Q'),
                gtk.gdk.CONTROL_MASK,
                gtk.ACCEL_VISIBLE)
        quit_item.connect('activate', self.quit)
        quit_item.show()

        file_menu = gtk.Menu()
        file_menu.append(open_item)
        file_menu.append(quit_item)

        file_item = gtk.MenuItem('_File')
        file_item.set_submenu(file_menu)
        file_item.show()

        menu_bar = gtk.MenuBar()
        menu_bar.show()
        menu_bar.append(file_item)

        box.pack_start(menu_bar, expand=False, fill=True, padding=0)

        scroller = gtk.ScrolledWindow()
        scroller.add(self.browser)
        box.pack_start(scroller, expand=True, fill=True, padding=0)

        window.set_default_size(832, 500)
        window.show_all()

    def quit(self, *args, **kwargs):
        message_queue.put(QuitApp)

    def open(self, *args, **kwargs):
        import gtk
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN, 
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name('HWP 5.0 files')
        filter.add_pattern('*.hwp')
        chooser.add_filter(filter)
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            message_queue.put(lambda: self.open_file(filename))
        chooser.destroy()

    def open_file(self, filename):
        synchronous_gtk_message(self.browser.execute_script)('document.write("<h2>Loading...</h2>")')
        uri = prepare_hwp_html(filename, self.working_dir)
        synchronous_gtk_message(self.browser.open)(uri)

    @companion_gtk_thread
    def main(self):
        self.make_frame()

        import tempfile
        self.working_dir = tempfile.mkdtemp()
        try:
            import sys
            if len(sys.argv) > 1:
                self.open_file(sys.argv[1])

            while True:
                msg = message_queue.get()
                if msg is QuitApp:
                    break
                msg()

        finally:
            import shutil
            shutil.rmtree(self.working_dir)

if __name__ == '__main__': # <-- this line is optional
    app = MainApp()
    app.main()
