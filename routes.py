from utils import log
from models.message import Message
from models.user import User
from models.session import Session

import random


def random_string():
    seed = 'kjlkjlkjlkljlkjkl'
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def template(name):
    """
    根据名字读取 templates 文件夹里的一个文件并返回
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def error(request, code=404):
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
        302: b'HTTP/1.x 302 Moved Permanently\r\nContent-Type: text/html\r\n'
             b'Location: localhost:3000/login\r\n\r\n'
    }
    return e.get(code, b'')


def current_user(request):
    # username = request.cookies.get('user', User.guest())
    session_id = request.cookies.get('session_id', '')
    s = Session.find_all()
    for session in s:
        log('session', session)
        if session.session_id == session_id:
            return session.username
    return User.guest()


def response_with_headers(headers):
    header = 'HTTP/1.x 210 VERY OK\r\n'
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.x 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    username = current_user(request)
    body = body.replace('{{username}}', username)
    r = header + '\r\n' + body
    return r.encode()


def route_login(request):
    """
    登录页面的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    username = current_user(request)
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            # 下面是把用户名存入 cookie 中
            # headers['Set-Cookie'] = 'user={}'.format(u.username)
            # session 会话
            # token 令牌
            # 设置一个随机字符串来当令牌使用
            session_id = random_string()
            data = dict(
                session_id=session_id,
                username=u.username
            )
            s = Session.new(data)
            s.save()
            headers['Set-Cookie'] = 'session_id={}'.format(session_id)
            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''

    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    # 1. response header
    # 2. headers
    # 3. body
    header = response_with_headers(headers)
    r = '{}\r\n{}'.format(header, body)
    log('login 的响应', r)
    return r.encode()


def route_register(request):
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    r = header + '\r\n' + body
    return r.encode()


def route_message(request):
    """
    主页的处理函数, 返回主页的响应
    """
    username = current_user(request)
    # if username == '【游客】':
    if username == User.guest():
        return error(request)
    else:
        log('本次请求的 method', request.method)
        if request.method == 'POST':
            data = request.form()
        else:
            data = request.query

        if len(data) > 0:
            log('post', data)
            m = Message.new(data)
            m.save()
            # message_list.append(data)

        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
        body = template('messages.html')
        ms = '<br>'.join([str(m) for m in Message.all()])
        body = body.replace('{{messages}}', ms)
        r = header + '\r\n' + body
        return r.encode()


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    filename = request.query['file']
    path = 'static/{}'.format(filename)
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        r = header + b'\r\n' + f.read()
        return r


def route_profile(request):
    from models.user import User
    username = current_user(request)
    if username == User.guest():
        return error(request, 302)
    else:
        user = User.find_by(username=username)
        header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
        body = template('profile.html')
        body = body.replace('{{id}}', str(user.id))
        body = body.replace('{{username}}', user.username)
        body = body.replace('{{note}}', user.note)
        r = header + '\r\n' + body
        return r.encode()


def route_dict():
    d = {
        '/': route_index,
        '/static': route_static,
        '/login': route_login,
        '/register': route_register,
        '/messages': route_message,
        '/profile': route_profile,
    }
    return d
