from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import mimetypes
import pathlib


BASE_DIR = pathlib.Path()
print(BASE_DIR)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        
        route  = urllib.parse.urlparse(self.path)
        print(route.params)

        match route.path:
            case '/':
                        
                self._render_html('storage/index.html')
            case '/message':
                self._render_html('storage/message.html')
            case _:
                self._render_html('storage/error.html', 404)
                file = BASE_DIR / route.path[1:]
                print(file)
                if file.exists:
                    self.send_css(file)
        
        self.send_css('storage/static.logo.py')


    def _render_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_css(self, filename):
        self.send_response(200)
        
        mime_type, *rest = mimetypes.guess_type(filename)

        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'text/plain')

        self.end_headers()

        with open(filename, 'rb') as file:
            self.wfile.write(file.read())



def run_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server running...')
    httpd.serve_forever()

run_server()
