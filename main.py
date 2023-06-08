from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import socket
from threading import Thread
import mimetypes
import pathlib
import json
from datetime import datetime
import logging



BASE_DIR = pathlib.Path().resolve()
print(f"BASE DIR{BASE_DIR}")
SERVER_IP = '127.0.0.1'
HTTP_PORT = 3000
SOCKET_PORT = 5000
BUFFER = 1024



class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        
        route  = urllib.parse.urlparse(self.path)
        print(route.params)
        print(f"PATh {route.path}")
        match route.path:
            case '/':
                self._render_html('index.html')
            case '/message':
                self._render_html('message.html')
            case _:
                if pathlib.Path().joinpath(route.path[1:]).exists():
                    self.send_css()
                else:
                    self._render_html('error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            self.send_data_to_socket(post_data)
            self.send_response(302)
            self.send_header('Location', '/message')
            self.end_headers()

    def send_data_to_socket(self, data):
        # print(data)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SERVER_IP, SOCKET_PORT))
        client_socket.close()

    def _render_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_css(self):
        self.send_response(200)
        
        mime_type, *rest = mimetypes.guess_type(self.path)

        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'text/plain')

        self.end_headers()
        print(BASE_DIR/self.path)
        try:
            with open(f".{self.path}", 'rb') as file:
                self.wfile.write(file.read())
        except FileNotFoundError:
            with open(f".{self.path.replace('.', '', 1)}", 'rb') as file:
                self.wfile.write(file.read())


def save_date(data):
    print('Save data : ',data)
    data = urllib.parse.unquote_plus(data.decode())
    message_time = str(datetime.now())

    try:
        pyload = {
            key: value for key, value in [el.split('=') for el in data.split('&')]
            }
        payload = {message_time: pyload}
        json_file_name = BASE_DIR.joinpath("data/data.json")
        if json_file_name.stat().st_size > 0:
            with open(json_file_name, "r", encoding="utf-8") as f:
                json_dict = json.load(f)
        else:
            json_dict = {}
        json_dict.update(payload)
        print(json_dict)
        with open(json_file_name, "w", encoding="utf-8") as f:
            json.dump(json_dict, f, ensure_ascii=False, indent=4)
    except ValueError as err:
        logging.error(f"Field parse data {data} with {err}")
    except OSError as err:
        logging.error(f"Field write data {data} with {err}")


socket_host = socket.gethostname()

def run_socket_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))

    try:
        while True:
            data, *adress = server_socket.recvfrom(BUFFER)
            save_date(data)
    except KeyboardInterrupt:
        logging.info("Socket server stopped")
    finally:
        server_socket.close


def run_server():
    server_address = ('', HTTP_PORT)
    http = HTTPServer(server_address, MyHandler)
    print('Server running...')
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")
    thread_server = Thread(target=run_server)
    thread_server.start()

    thread_socket = Thread(target=run_socket_server, args=(SERVER_IP, SOCKET_PORT))
    thread_socket.start()