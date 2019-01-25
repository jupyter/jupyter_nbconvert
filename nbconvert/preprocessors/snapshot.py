"""PreProcessor for rendering """

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import os
import copy
import tempfile
import webbrowser
import threading
import tornado.escape
import nbformat

from traitlets.config.configurable import LoggingConfigurable
from tornado import web, ioloop, httpserver, log
from tornado.httpclient import AsyncHTTPClient
from traitlets import Bool, Unicode, Int, DottedObjectName, Type, observe, Instance
from traitlets.utils.importstring import import_item


from .base import Preprocessor
from ..exporters.html import HTMLExporter
from ..writers import FilesWriter


class SnapshotHandler(web.RequestHandler):
    def initialize(self, snapshot_dict, callback):
        self.snapshot_dict = snapshot_dict
        self.callback = callback

    # @web.asynchronous
    def post(self, view_id=None, image_data=None):
        #, view_id=None, image_data=None
        #view_id = self.get_parameter('view_id')
        data = tornado.escape.json_decode(self.request.body)
        #print('hi', data['cell_index'], data['output_index'])
        i, j = data['cell_index'], data['output_index']
        key = i, j
        image_data = data['image_data']
        header = 'data:image/png;base64,'
        assert image_data.startswith(header), 'not a png image?'
        self.snapshot_dict[key]['data'][MIME_TYPE_PNG] = image_data[len(header):]
        self.callback()


MIME_TYPE_JUPYTER_WIDGET_VIEW = 'application/vnd.jupyter.widget-view+json'
MIME_TYPE_PNG = 'image/png'
MIME_TYPE_HTML = 'text/html'
DIRNAME_STATIC = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources'))
def next_port():
    i = 8009
    while 1:
        yield i
        i += 1

next_port = next_port()

class PageOpener(LoggingConfigurable):
    pass

class PageOpenerDefault(PageOpener):
    browser = Unicode(u'', 
                      help="""Specify what browser should be used to open slides. See
                      https://docs.python.org/3/library/webbrowser.html#webbrowser.register
                      to see how keys are mapped to browser executables. If 
                      not specified, the default browser will be determined 
                      by the `webbrowser` 
                      standard library module, which allows setting of the BROWSER 
                      environment variable to override it.
                      """).tag(config=True)

    def open(self, url):
        browser = webbrowser.get(self.browser or None)
        b = lambda: browser.open(url, new=2)
        threading.Thread(target=b).start()

chrome_binary = 'echo "not found"'
import platform
if platform.system().lower() == 'darwin':
    chrome_binary = r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
elif platform.system().lower() == 'linux':
    chrome_binary = 'google-chrome'




class PageOpenerChromeHeadless(PageOpener):
    start_command = Unicode('%s --remote-debugging-port=9222 --headless &' % chrome_binary).tag(config=True)
    def open(self, url):
        import PyChromeDevTools
        import requests.exceptions
        import time
        try:
            chrome = PyChromeDevTools.ChromeInterface()
        except requests.exceptions.ConnectionError:
            print('could not connect, try starting with', self.start_command)
            ret = os.system(self.start_command)
            if ret != 0:
                raise ValueError('could not start chrome headless with command: ' + self.start_command)
            for i in range(4):
                time.sleep(1)
                print('try connecting to chrome')
                try:
                    chrome = PyChromeDevTools.ChromeInterface()
                except requests.exceptions.ConnectionError:
                    if i == 3:
                        raise
        chrome.Network.enable()
        chrome.Page.enable()
        chrome.Page.navigate(url=url)


# chrome caches the js files, bad for development
class StaticFileHandlerNoCache(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


class SnapshotPreProcessor(Preprocessor):
    """Pre processor that will make snapshots of widgets and html
    """

    open_in_browser = Bool(True,
        help="""Should the browser be opened automatically?"""
    ).tag(config=True)
    devmode = Bool(True,
        help="""In dev mode, the static files will not be cached by the browser"""
    ).tag(config=True)
    keep_running = Bool(False, help="Keep server running when done").tag(config=True)
    page_opener = Instance(PageOpener).tag(config=True)
    page_opener_class = DottedObjectName('nbconvert.preprocessors.snapshot.PageOpenerChromeHeadless',
                                    help="""How to open a page for rendering""").tag(config=True)
    page_opener_aliases = {'headless': 'nbconvert.preprocessors.snapshot.PageOpenerChromeHeadless',
                           'default': 'nbconvert.preprocessors.snapshot.PageOpenerDefault'}
    page_opener_factory = Type(allow_none=True)

    @observe('page_opener_class')
    def _page_opener_class_changed(self, change):
        new = change['new']
        if new.lower() in self.page_opener_aliases:
            new = self.page_opener_aliases[new.lower()]
        self.page_opener_factory = import_item(new)

    ip = Unicode("127.0.0.1",
                 help="The IP address to listen on.").tag(config=True)
    port = Int(8000, help="port for the server to listen on.").tag(config=True)

    def callback(self):
        done = True
        for key, value in self.snapshot_dict.items():
            if value['data'][MIME_TYPE_PNG] is None:
                done = False

        if done and not self.keep_running:
            self.stop_server()

    # see https://github.com/tornadoweb/tornado/issues/2523
    def stop_server(self):
        self.http_server.stop()
        self.main_ioloop.add_future(self.http_server.close_all_connections(),
                                    lambda x: self.main_ioloop.stop())

    def preprocess(self, nb, resources):
        """Serve the build directory with a webserver."""
        self.snapshot_dict = {}
        self.nb = nb
        for cell_index, cell in enumerate(self.nb.cells):
            if 'outputs' in cell:
                for output_index, output in enumerate(cell.outputs):
                    if 'data' in output:
                        if MIME_TYPE_JUPYTER_WIDGET_VIEW in output['data'] or MIME_TYPE_HTML in output['data']:
                            # clear the existing png data, we may consider skipping these cells
                            output['data'][MIME_TYPE_PNG] = None
                            self.snapshot_dict[(cell_index, output_index)] = output
        if self.snapshot_dict.keys():
            with tempfile.TemporaryDirectory() as dirname:
                html_exporter = HTMLExporter(template_file='snapshot', default_preprocessors=[
                                      'nbconvert.preprocessors.SVG2PDFPreprocessor',
                                      'nbconvert.preprocessors.CSSHTMLHeaderPreprocessor',
                                      'nbconvert.preprocessors.HighlightMagicsPreprocessor',
                                  ])
                nbc =  copy.deepcopy(nb)
                resc = copy.deepcopy(resources)
                output, resources_html = html_exporter.from_notebook_node(nbc, resources=resc)
                writer = FilesWriter(build_directory=dirname)
                filename_base = 'index'
                filename = filename_base + '.html'
                writer.write(output, resources_html, notebook_name=filename_base)

                # dirname, filename = os.path.split(input)
                handlers = [
                    (r"/send_snapshot", SnapshotHandler, dict(snapshot_dict=self.snapshot_dict, callback=self.callback)),
                    (r"/resources/(.+)", StaticFileHandlerNoCache if self.devmode else web.StaticFileHandler,
                                            {'path' : DIRNAME_STATIC}),
                    (r"/(.+)", web.StaticFileHandler, {'path' : dirname}),
                    (r"/", web.RedirectHandler, {"url": "/%s" % filename})
                ]
                app = web.Application(handlers,
                                      client=AsyncHTTPClient(),
                                      )
                
                # hook up tornado logger to our logger
                log.app_log = self.log

                self.http_server = httpserver.HTTPServer(app)
                self.http_server.listen(self.port, address=self.ip)
                url = "http://%s:%i/%s" % (self.ip, self.port, filename)
                print("Serving your slides at %s" % url)
                print("Use Control-C to stop this server")
                self.main_ioloop = ioloop.IOLoop.instance()
                if self.open_in_browser:
                    self._page_opener_class_changed({ 'new': self.page_opener_class })
                    self.page_opener = self.page_opener_factory()
                    self.page_opener.open(url)
                try:
                    self.main_ioloop.start()
                except KeyboardInterrupt:
                    print("\nInterrupted")
                    self.http_server.stop()
                    # TODO: maybe we need to wait for this to finish
                    self.http_server.close_all_connections()
                # nbformat.write(self.nb, input.replace('.html', '.ipynb'))
        return nb, resources

def main(path):
    """allow running this module to serve the slides"""
    server = SnapshotPreProcessor()
    server(path)
    
if __name__ == '__main__':
    import sys
    main(sys.argv[1])
