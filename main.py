from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import threading
import socket
import datetime
import json

def send_to_JSON(data:dict = {}):
    print('_____SEND_TO_JSON_____')
    path_file = str(pathlib.Path.cwd()) + r'\front-init\front-init\storage\data.json'
    bool_path = pathlib.Path(path_file)
    
    if not bool_path.exists():
        with open(path_file, 'w') as f:
            json.dump(data, f, indent=2)

    else:
        
        with open(path_file) as f:
            js = json.load(f)
         
        js.update(data)  
        
        with open(path_file, 'w') as f:
            json.dump(js, f, indent=2)






def send_data_to_server(data:dict):
    UDP_IP = '127.0.0.1'
    UDP_PORT = 5000
    key = datetime.datetime.now()

    data['message'] = data['message'] + ' STOP_WORD'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
    for line in data['message'].split(' '):
        
         msg = f'{key}__{data["username"]}__{line}'.encode()
         sock.sendto(msg, server)

    sock.close()


class HttpHandler(BaseHTTPRequestHandler):

    # path_front_init = r'D:\Github\WEB_modul4\front-init\front-init\\'  # це не вірно, треба задати відносний шлях, бо не буде працювати в докері та на сервері
    path_front_init = str(pathlib.Path.cwd()) + r'\front-init\front-init\\'  # ось так створимо шлях до поточної директорії
    

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == '/':
            
            self.send_html_file(self.path_front_init + 'index.html')  # просто шлях до файлу

        elif pr_url.path == '/message.html':
            self.send_html_file(self.path_front_init + 'message.html')

        else:
            print(pr_url.path[1:])
            if pathlib.Path().joinpath(self.path_front_init + '\\' + pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file(self.path_front_init + 'error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        
        with open(self.path_front_init + '\\' + self.path[1:], 'rb') as file:
             self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())

        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        run_client_srv = threading.Thread(target=send_data_to_server, args=(data_dict,))
        run_client_srv.start()
        run_client_srv.join()
        
        #send_data_to_socket(data_dict) # тут тепер треба викликати функцію send_data_to_socket(data_dict) - яка передає данні на сервер
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_server():
    UDP_IP = '127.0.0.1'
    UDP_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
    sock.bind(server)
    sock_str = {}
    try:
        
        while True:
            data, adress = sock.recvfrom(1024)
            #sock_str += data['massege']
            data_list = data.decode().split('__')
            key = data_list[0]
            username = data_list[1]
            msg_word = data_list[2]

         
            if key not in sock_str:
                sock_str[key] = {'adress': adress[1], username: msg_word}
            
            else:
                if msg_word == 'STOP_WORD' and adress[1] == sock_str[key]['adress']:
        
                    result = {key:{'username': username, 'message': sock_str[key][username]}}
                    send_to_JSON(result)
                    print(result)
                    del sock_str[key]
                else:
                    sock_str[key][username] += f' {msg_word}'
            
            
    except:
        pass
    finally:
        sock.close()


if __name__ == '__main__':
    run_ = threading.Thread(target=run)
    
    server = threading.Thread(target=run_server)
    run_.start()
    server.start()
    server.join()
    run_.join()


    