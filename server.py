import _thread
import socket
import urllib.parse
import _thread

from routes import route_dict
from routes import route_static, error
from utils import log


class Request(object):
    def __init__(self):
        self.raw_data = ''
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_headers(self, header):
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            k, v = cookies.split('=', 1)
            self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


def parsed_path(path):
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        query_string = path[index + 1:]
        p = path[:index]
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return p, query


def response_for_request(request):
    request.path, request.query = parsed_path(request.path)
    log('path 和 query', request.path, request.query)
    r = route_dict()
    response = r.get(request.path, error)
    return response(request)


def process_connection(connection):
    with connection:
        r = connection.recv(1024)
        r = r.decode()
        log('request {}'.format(r))
        if len(r) > 0:
            # 把 body 放入 request 中
            request = Request()
            request.raw_data = r
            # 只能 split 一次，因为 body 中可能有换行
            header, request.body = r.split('\r\n\r\n', 1)
            h = header.split('\r\n')
            parts = h[0].split()
            request.path = parts[1]
            # 设置 request 的 method
            request.method = parts[0]
            request.add_headers(h[1:])

            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_request(request)
            # 把响应发送给客户端
            connection.sendall(response)
        else:
            log('接收到了一个空请求')


def run(host, port):
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        # 监听 接受 读取请求数据 解码成字符串
        s.listen()
        while True:
            connection, address = s.accept()
            log('ip <{}>\n'.format(address))
            _thread.start_new_thread(process_connection, (connection,))


if __name__ == '__main__':
    config = dict(
        host='localhost',
        port=3000,
    )
    run(**config)
