from wsgiref.simple_server import make_server


def parse_params(params: str):
    answer = {}
    params_list = params.split('&')
    for param in params_list:
        if param == '':
            continue
        pos = param.find('=')
        key = param[ : pos]
        value = param[pos + 1 : ]
        answer[key] = value
    return answer


def simple_app(environ, start_response):
    get_params = parse_params(environ.get('QUERY_STRING') or '')
    post_params = parse_params(environ['wsgi.input'].read().decode())

    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)

    response = f'GET parameters: {get_params}\nPOST parameters: {post_params}\n'
    print(response)
    return [response.encode()]


if __name__ == '__main__':
    server = make_server('localhost', 8081, simple_app)
    server.serve_forever()