import ssl
import socket


def parsed_url(url):
    separator = '://'
    i = url.find(separator)
    if i == -1:
        protocol = 'http'
        u = url
    else:
        protocol = url[:i]
        u = url[i + len(separator):]
    print('protocol and u', protocol, u)

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    i = host.find(':')
    if i == -1:
        # 检查端口
        # 表驱动法
        port_dict = {
            'http': 80,
            'https': 443,
        }
        # 默认端口
        port = port_dict[protocol]
        # if protocol == 'http':
        #     port = 80
        # elif protocol == 'https':
        #     port = 443
        # else
        #   error
        #
        # if protocol == 'http':
        #     port = 80
        # else:
        #     port = 443
    else:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def parsed_response(r):
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v

    return status_code, headers, body


def response_by_socket(s):
    response = b''
    buffer_size = 1024
    while True:
        print('new loop')
        r = s.recv(buffer_size)
        print('response', len(r), r)
        response += r
        if len(r) < buffer_size:
            return response


def socket_by_protocol(protocol):
    s = socket.socket()
    if protocol == 'https':
        return ssl.wrap_socket(s)
    else:
        return s


# 复杂的逻辑全部封装成函数

def get(url):
    protocol, host, port, path = parsed_url(url)
    print('log request', protocol, host, port, path)

    s = socket_by_protocol(protocol)
    s.connect((host, port))

    # Connection 有两个选项 close 和 keep-alive
    # 要么就一次 recv 所有数据
    # 要么就用无限循环加 Connection: close
    # '' % path
    request = 'GET {} HTTP/1.1\r\nHost: {}\r\nCookie: session_id=kjjjklkkkljjkkjk\r\n\r\n'.format(path, host)
    # encode 的 'utf-8' 参数可以省略
    s.send(request.encode())

    response = response_by_socket(s)
    r = response.decode()
    print('response:\n', r)
    status_code, headers, body = parsed_response(r)

    if status_code == 301:
        url = headers['Location']
        return get(url)
    else:
        return response, status_code


def main():
    # url = 'http://movie.douban.com/top250'
    url = 'http://localhost:3000/login'
    response, status_code = get(url)
    # decode 的 'utf-8' 参数可以省略
    print(response.decode())


# 以下 test 开头的函数是单元测试
def test_parsed_url():
    http = 'http'
    https = 'https'
    host = 'g.cn'
    path = '/'
    test_items = [
        ('http://g.cn', (http, host, 80, path)),
        ('http://g.cn/', (http, host, 80, path)),
        ('http://g.cn:90', (http, host, 90, path)),
        ('http://g.cn:90/', (http, host, 90, path)),
        #
        ('https://g.cn', (https, host, 443, path)),
        ('https://g.cn:233/', (https, host, 233, path)),
    ]
    for t in test_items:
        url, expected = t
        u = parsed_url(url)
        e = "parsed_url ERROR, ({}) ({}) ({})".format(
            url, u, expected
        )
        # assert 1==2, '1 is not equal to 2'
        assert u == expected, e


def test_get():
    url = 'http://movie.douban.com/top250'
    response, status_code = get(url)
    expected = 200
    e = "get ERROR, ({}) ({}) ({}) ({})".format(
        url, response, status_code, expected
    )
    assert expected == status_code, e


def test():
    test_parsed_url()
    test_get()


if __name__ == '__main__':
    # test()
    main()

